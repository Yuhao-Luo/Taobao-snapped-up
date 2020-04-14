# -*- coding: utf-8 -*-

# 使用教程：
# 1.使用chrome浏览器并下载对应版本号的chromedriver驱动:http://chromedriver.storage.googleapis.com/index.html
# 2.https://account.weibo.com/set/bindsns/bindtaobao 通过微博绑定淘宝账号密码
# 3.填写chromedriver的绝对路径
# 4.运行程序


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import time

# ==== 设定抢购时间 （修改此处，指定抢购时间点）====
BUY_TIME = "2020-04-14 20:00:00"

buy_time_object = datetime.datetime.strptime(BUY_TIME, '%Y-%m-%d %H:%M:%S')
now_time = datetime.datetime.now()

#定义一个taobao类
class taobao_infos:

    #对象初始化
    def __init__(self):
        url = 'https://login.taobao.com/member/login.jhtml'
        self.url = url

        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # 不加载图片,加快访问速度
        options.add_experimental_option('excludeSwitches', ['enable-automation']) # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium

        self.browser = webdriver.Chrome(executable_path=chromedriver_path, options=options)
        self.wait = WebDriverWait(self.browser, 10) #超时时长为10s

    #登录淘宝
    def login(self):

        # 打开网页
        self.browser.get(self.url)

        # 等待 密码登录选项 出现
        # password_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.qrcode-login > .login-links > .forget-pwd')))
        # password_login.click()

        # 等待 微博登录选项 出现
        weibo_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
        weibo_login.click()

        # 等待 微博账号 出现
        weibo_user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.username > .W_input')))
        weibo_user.send_keys(weibo_username)

        # 等待 微博密码 出现
        weibo_pwd = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.password > .W_input')))
        weibo_pwd.send_keys(weibo_password)

        # 等待 登录按钮 出现
        submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn_tip > a > span')))
        submit.click()

        # 直到获取到淘宝会员昵称才能确定是登录成功
        taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
        # 输出淘宝昵称
        print(taobao_name.text + " login in success")

    #保持登陆状态
    def keep_login_and_wait(self):
        print("距离抢购时间点还有较长时间，开始定时刷新防止登录超时...")
        while True:
            currentTime = datetime.datetime.now()
            if (buy_time_object - currentTime).seconds > 180:
                self.browser.get("https://cart.taobao.com/cart.htm")
                print("刷新购物车界面，防止登录超时...")
                time.sleep(60)
            else:
                break

    #清空购物车
    def buy(self):
        #打开购物车
        self.browser.get("https://cart.taobao.com/cart.htm")
    
        #点击购物车里全选按钮
        if self.browser.find_element_by_id("J_SelectAll1"):
            self.browser.find_element_by_id("J_SelectAll1").click()
            print("已经选中购物车中全部商品 ...")

        submit_succ = False
        retry_submit_times = 0
        while True:
            now = datetime.datetime.now()
            if now >= buy_time_object:
                print("到达抢购时间，开始执行抢购...尝试次数：" + str(retry_submit_times))
                if submit_succ:
                    print("订单已经提交成功，无需继续抢购...")
                    break
                if retry_submit_times > 50:
                    print("重试抢购次数达到上限，放弃重试...")
                    break

                try:
                    #点击结算按钮
                    if self.browser.find_element_by_id("J_Go"):
                        self.browser.find_element_by_id("J_Go").click()
                        print("已经点击结算按钮...")
                        click_submit_times = 0
                        while True:
                            try:
                                if click_submit_times < 100:
                                    self.browser.find_element_by_link_text('提交订单').click()
                                    print("已经点击提交订单按钮")
                                    submit_succ = True
                                    break
                                else:
                                    print("提交订单失败...")
                                    click_submit_times = 0
                            except Exception as ee:
                                #print(ee)
                                print("没发现提交订单按钮，可能页面还没加载出来，重试...")
                                click_submit_times = click_submit_times + 1
                                time.sleep(0.1)
                except Exception as e:
                    print(e)
                    print("不好，挂了，提交订单失败了...")

            time.sleep(0.1)

if __name__ == "__main__":
    
    chromedriver_path = "users/ChromeDriverPath/chromedriver.exe" #改成你的chromedriver的完整路径地址
    weibo_username = "username" #改成你的微博账号
    weibo_password = "password" #改成你的微博密码

    a = taobao_infos()
    a.login()
    a.keep_login_and_wait()
    a.buy()
