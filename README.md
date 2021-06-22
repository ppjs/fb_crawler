# fb_crawler

fb自從API的審核變嚴格之後，一般人不能再利用API抓取公開的資料<br/>
fb_crawler利用爬蟲的方式，透過mbasic.facebook.com抓貼文的的所有留言<br/>
由於需要登入後才能抓去，因此需要提供<br/>
-mail: 帳號<br/>
-passwd: 密碼<br/>
-url: 要抓的貼文連結<br/>
＊要注意一次抓太多資料的話，帳號有可能會被FB給鎖定<br/>
<br/>
輸出資訊包含<br/>
-userID: 使用者的fb profile ID<br/>
-userName: 使用者姓名<br/>
-commentContent: 留言的內容 <br/>
-commentTime: 留言日期
