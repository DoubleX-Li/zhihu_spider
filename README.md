想写一个知乎的爬虫

目前解决的问题：
- [x] 模拟登陆
- [x] 读取特定用户信息
- [x] 跟随关注链读取用户信息
- [x] 获取特定用户回答
- [x] 只能获取到用户的最新两条回答，网页源代码与看到的页面不一致？（使用PhantomJS解决了）

目前遇到的困难：
- [ ] 没有单独的用户信息页面，有些用户信息不易获取
- [ ] PhantomJS阻塞了Scrapy框架
