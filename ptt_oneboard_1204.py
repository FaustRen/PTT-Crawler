#%%
import pandas as pd
import numpy as np
import requests
import datetime
from bs4 import BeautifulSoup
from IPython.display import display as display
ptt_url_head="https://www.ptt.cc/"
todayRoot = datetime.date.today().strftime("%m/%d").lstrip('0')

class LineNotify:
    """Line 傳送訊息"""
    def __init__(self, token, message):
        """Line權杖、要傳送的訊息"""
        self.token = token
        self.message=message
        
    def sendMessage(self):
        """傳送訊息"""
        line_url="https://notify-api.line.me/api/notify"  ## Line 通知熱門文章：
        for _ in range(10):
            requests.post(url=line_url,headers={'Authorization':f'Bearer {self.token}'},data={"message":self.message})
    
    def showPrep(self):
        """show stuff"""
        print(f"Token={self.token}")
        print(f"Message={self.message}")


class PTT:
    """Ptt - doc"""
    def __init__(self,url_board,threshold):
        """PTT連結"""
        self.url_board = url_board
        self.threshold = threshold
    
    def showPttStuff(self):
        """print準備的東西"""
        print(f"Ptt_link={self.url_board}")
        
    def getPageInfo(self,url_input):
        """request 外頁"""
        ptturl=url_input
        res = requests.get(url=ptturl, cookies={"over18":"1"})
        if res.status_code==200:
            return res.text
        else:
            print(f"Error! status code={res.status_code}")
            return None
    
    def getTweets(self, content_url_input):
        """取得文章下面的推文"""
        cookies= {'over18':"1"}
        response = requests.get(url=content_url_input, cookies=cookies)
        soup = BeautifulSoup(response.text, 'html5lib')         # 整理原始碼
        articles = soup.find_all('div', 'push')
        return articles
    
    def countElements(self, articles_input):
        """判斷每一則推文屬於: 推/噓/→"""
        articles = articles_input
        # print(f"參與人數: {len(articles)}")
        push_count,boo_count,arrow_count=0,0,0
        for i in range(len(articles)):# 判斷每一則推文屬於..推/噓/→
            if articles[i].find("span", attrs={"class":"hl push-tag"}):#推文result分兩種
                push_res=articles[i].find("span", attrs={"class":"hl push-tag"}).text
            if articles[i].find("span", attrs={"class":"f1 hl push-tag"}):#f1 hl push-tag
                push_res=articles[i].find("span", attrs={"class":"f1 hl push-tag"}).text
            
            if '推' in str(push_res):
                push_count+=1
            if '→' in str(push_res):
                arrow_count+=1
            if '噓' in str(push_res):
                boo_count+=1
        # print(push_count,boo_count,arrow_count)
        return push_count,boo_count,arrow_count,    
    
    
    def getArticles(self,page_text):
        """外頁資訊"""
        soup = BeautifulSoup(page_text, 'html5lib')
        prev_url = soup.select('.btn-group-paging a')[1]['href']#上一頁連結
        prev_url="https://www.ptt.cc"+prev_url
        # 搜尋每一篇文章
        divs = soup.find_all(class_="r-ent")
        articles=[]
        # 外頁的每一篇文
        for i in range(len(divs)):
            try:
                if (divs[i].find(class_="meta").find(class_="author").getText()):#有時會遇到文章被刪掉,那時就get不到東西,於是會error
                    content_link = str(ptt_url_head+divs[i].find(class_="title").select_one("a").get("href"))#文章連結
                    content_title = (divs[i].find(class_="title").select_one("a").getText())#文章標題
                    content_author = (divs[i].find(class_="meta").find(class_="author").getText())#作者
                    content_date = (divs[i].find(class_="meta").find(class_="date").getText())#日期
                    # print(content_link)
                    if content_date == todayRoot:
                        alltweets = self.getTweets(content_link)
                        print(len(alltweets))
                        ##  設定門檻, 如果參與人數達標才計算推噓  ##
                        if len(alltweets)<self.threshold:
                            continue
                        else:
                            content_push,content_boo,content_arrow=self.countElements(alltweets)
                            content_total=content_push+content_boo+content_arrow
                            articles.append({
                                "title":content_title,
                                "href":content_link,
                                "author":content_author,
                                "Push":content_push,
                                "Boo":content_boo,
                                "Arrow":content_arrow,
                                "Total":content_total
                            })
                # break
            except:return articles,prev_url
        return articles,prev_url
    
    def allArticles(self,url_input):
        """get 全部的文"""
        current_page = self.getPageInfo(url_input)#最新日期的page
        articles,prev_url=self.getArticles(current_page)#最新日期的page
        all_articles = []
        while articles:
            all_articles +=articles
            current_page =self.getPageInfo(prev_url)#目前爬取的page
            articles,prev_url = self.getArticles(current_page)#prev_url=next page
        return all_articles
            
    def excute(self,):
        url = self.url_board
        all_articles=self.allArticles(url)
        df_ptt = pd.DataFrame(all_articles)
        return df_ptt
        
            

    
    
link_gossiping = "https://www.ptt.cc/bbs/Gossiping/index.html"
link_nba="https://www.ptt.cc/bbs/NBA/index.html"
ptt = PTT(url_board=link_nba,threshold=60)
ptt_df=ptt.excute()
display(ptt_df)
## 爬蟲通知
token_input = "s9xxSvjoSEHvR9xOn7OtJBs4AYj0Ya5VH3xAcfvCpqw"
line = LineNotify(token=token_input,message="爬完了老弟")
line.sendMessage()


# token_input = "AzEXAL6osYPjBXgFI0RAcOdlwJ4n4t2a0XWxjp4z4ah"

