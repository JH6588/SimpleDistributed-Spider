import subprocess
import time


def screen_process(x,n):
    d = subprocess.run ("ps -ef|grep {}".format(x) ,stdout =subprocess.PIPE ,shell =True)
    dr = d.stdout.decode()
    m =dr.count(x)
    print(m,"个进程")
    while m <n:
        subprocess.Popen("python {}".format(x) ,shell =True)
        m +=1
        print("启动,还要启动{}".format(n-m))
        time.sleep(20)


if __name__ == '__main__':
    while True:
        screen_process("gj/gj_run.py",10)
        time.sleep(60)
