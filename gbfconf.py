import math
import os
fk=10
fk2=int(fk/2)
tempfl='''
R{routernum}
# This file describes the network interfaces
'''
tempfm='''
auto R{routernum}-eth{ethnum}
iface R{routernum}-eth{ethnum} inet static
address {addr}
'''
tempfr='''
# ports.conf --
'''

templatel='''
frr version 10.3
frr defaults traditional
log file /tmp/R{routernum}.log
ip forwarding
no ipv6 forwarding
hostname R{routernum}
service integrated-vtysh-config
!
route-map ALLOW_ALL permit 10
!
password zebra
enable password zebra
!
router bgp {asnum}
  bgp router-id {routerip}
  bgp bestpath as-path multipath-relax
'''

templatem='''
  neighbor {ip} remote-as {num}
  neighbor {ip} ebgp-multihop
  neighbor {ip} update-source {ethip}
'''
template_unil='''
  address-family ipv4 unicast
    network {netip}
'''
template_unil_nonet='''
  address-family ipv4 unicast
'''
template_aggr='''
    aggregate-address {aggrip} summary-only
'''
tasin='''
    neighbor {ip} allowas-in
'''
template_unim='''
    neighbor {ip} route-map ALLOW_ALL in
    neighbor {ip} route-map ALLOW_ALL out    
'''
template_unir='''
    maximum-paths 128
  exit-address-family
'''
templater='''
!
'''

tzebral='''
ip route {netip} Null0
'''
tzebram='''
interface R{routernum}-eth{ethnum}
  ip address {addr}
'''
tzebrar='''
line vty
'''
to_frr=False
def genftop(num,nums,ethself,ethother):
    retstr=""
    data={"routernum":num}
    retstr=retstr+tempfl.format(**data)
    for i in range(0,len(nums)):
        data={"routernum":num,
              "ethnum":i+1,
              "addr":"9.%s.%s.%s/24"%(num,ethself[i]+1,num)}
        retstr=retstr+tempfm.format(**data)
    retstr=retstr+tempfr
    return retstr

def genfbottom(num,nums,ethself,ethother):
    data={"routernum":num}
    retstr=tempfl.format(**data)
    for i in range(0,fk2):
        data={"routernum":num,
              "ethnum":i+1,
              "addr":"%s.0.%s.254/24"%(num+10+1,i+1)}
        retstr=retstr+tempfm.format(**data)
    for i in range(0,fk2):
        data={"routernum":num,
              "ethnum":fk2+i+1,
              "addr":"9.%s.%s.%s/24"%(nums[i],ethother[i]+1,num)}
        retstr=retstr+tempfm.format(**data)
    retstr=retstr+tempfr
    return retstr

def genfmid(num,nums,ethself,ethother):
    retstr=""
    data={"routernum":num}
    retstr=tempfl.format(**data)
    for i in range(0,fk2):
        data={"routernum":num,
              "ethnum":i+1,
              "addr":"9.%s.%s.%s/24"%(nums[i],ethother[i]+1,num)}
        retstr=retstr+tempfm.format(**data)
    for i in range(fk2,fk):
        data={"routernum":num,
              "ethnum":i+1,
              "addr":"9.%s.%s.%s/24"%(num,ethself[i]+1,num)}
        retstr=retstr+tempfm.format(**data)
    retstr=retstr+tempfr
    return retstr

####
def genbtop(num,nums,ethself,ethother):
    retstr=""
    data={"routernum":str(num),
          "routerip":"9.%s.%s.%s"%(num,fk,num),
          "asnum":65000}
    retstr=retstr+templatel.format(**data)
    for i in range(0,len(nums)):
        data={"ip":"9.%s.%s.%s"%(num,ethself[i]+1,nums[i]),
              "num":65100+ethself[i]+1,
              "ethip":"9.%s.%s.%s"%(num,ethself[i]+1,num)}
        retstr=retstr+templatem.format(**data)
    retstr=retstr+template_unil_nonet
    for i in range(0,len(nums)):
        data={"ip":"9.%s.%s.%s"%(num,ethself[i]+1,nums[i])}
        retstr=retstr+template_unim.format(**data)
    retstr=retstr+template_unir

    retstr=retstr+templater
    return retstr

def genbbottom(num,nums,ethself,ethother):
    num1=nums[0]
    e1=ethother[0]+1
    retstr=""
    data={"routernum":str(num),
          "routerip":"9.%s.%s.%s"%(num1,e1,num),
          "asnum":65200+num%fk2+1}
    retstr=retstr+templatel.format(**data)
    for i in range(0,len(nums)):
        data={"ip":"9.%s.%s.%s"%(nums[i],ethother[i]+1,nums[i]),
              "num":65100+1+math.floor(num/fk2),
              "ethip":"9.%s.%s.%s"%(nums[i],ethother[i]+1,num)}
        retstr=retstr+templatem.format(**data)
    podnum=int(num/fk2)
    inpodnum=num%fk2
    data={"netip":"%s.%s.0.0/16"%(11+podnum,11+inpodnum)}
    retstr=retstr+template_unil.format(**data)
    for i in range(0,len(nums)):
        data={"ip":"9.%s.%s.%s"%(nums[i],ethother[i]+1,nums[i])}
        retstr=retstr+tasin.format(**data)
        retstr=retstr+template_unim.format(**data)
    retstr=retstr+template_unir
    retstr=retstr+templater
    return retstr
#"netip":"%s.0.0.0/8"%(10+num+1),
def genbmid(num,nums,ethself,ethother):
    retstr=""
    data={"routernum":str(num),
          "routerip":"9.%s.%s.%s"%(num,fk,num),
          "asnum":65100+1+math.floor((num-fk*fk2)/fk2)}
    retstr=retstr+templatel.format(**data)
    for i in range(0,fk2):
        data={"ip":"9.%s.%s.%s"%(nums[i],ethother[i]+1,nums[i]),
              "num":65000,
              "ethip":"9.%s.%s.%s"%(nums[i],ethother[i]+1,num)}
        retstr=retstr+templatem.format(**data)
    for i in range(fk2,fk):
        data={"ip":"9.%s.%s.%s"%(num,ethself[i]+1,nums[i]),
              "num":65200+nums[i]%fk2+1,
              "ethip":"9.%s.%s.%s"%(num,ethself[i]+1,num)}
        retstr=retstr+templatem.format(**data)
    retstr=retstr+template_unil_nonet
    podnum=int((num-fk*fk2)/fk2)
    inpodnum=(num-fk*fk2)%fk2
    data={"aggrip":"%s.0.0.0/8"%(11+podnum)}
    retstr=retstr+template_aggr.format(**data)
    for i in range(0,fk2):
        data={"ip":"9.%s.%s.%s"%(nums[i],ethother[i]+1,nums[i])}
        retstr=retstr+template_unim.format(**data)

    for i in range(fk2,fk):
        data={"ip":"9.%s.%s.%s"%(num,ethself[i]+1,nums[i])}
        retstr=retstr+template_unim.format(**data)
    retstr=retstr+template_unir
    retstr=retstr+templater
    return retstr

#####

def genztop(num,nums,ethself,ethother):
    retstr=""
    data={"netip":"%s.0.0.0/8"%(10+num+1)}
    #retstr=retstr+tzebral.format(**data)
    for i in range(0,len(nums)):
        data={"routernum":num,
              "ethnum":i+1,
              "addr":"9.%s.%s.%s/24"%(num,ethself[i]+1,num)}
        retstr=retstr+tzebram.format(**data)
    retstr=retstr+tzebrar
    return retstr

def genzbottom(num,nums,ethself,ethother):
    podnum=int(num/fk2)
    inpodnum=num%fk2
    data={"netip":"%s.%s.0.0/16"%(11+podnum,11+inpodnum)}
    retstr=tzebral.format(**data)
    for i in range(0,fk2):
        podnum=int(num/fk2)
        inpodnum=num%fk2
        data={"routernum":num,
              "ethnum":i+1,
              "addr":"%s.%s.%s.254/24"%(podnum+11,inpodnum+11,i+1)}
        retstr=retstr+tzebram.format(**data)
    for i in range(0,fk2):
        data={"routernum":num,
              "ethnum":fk2+i+1,
              "addr":"9.%s.%s.%s/24"%(nums[i],ethother[i]+1,num)}
        retstr=retstr+tzebram.format(**data)
    retstr=retstr+tzebrar
    return retstr

def genzmid(num,nums,ethself,ethother):
    retstr=""
    data={"netip":"%s.0.0.0/8"%(10+num+1)}
    #retstr=tzebral.format(**data)
    for i in range(0,fk2):
        data={"routernum":num,
              "ethnum":i+1,
              "addr":"9.%s.%s.%s/24"%(nums[i],ethother[i]+1,num)}
        retstr=retstr+tzebram.format(**data)
    for i in range(fk2,fk):
        data={"routernum":num,
              "ethnum":i+1,
              "addr":"9.%s.%s.%s/24"%(num,ethself[i]+1,num)}
        retstr=retstr+tzebram.format(**data)
    retstr=retstr+tzebrar
    return retstr

def writefile(writestr,filename):
    with open(filename,"w") as f:
        f.write(writestr)


hjs='''

{{
	"hostname" : "{name}",
	"hostInterfaces" : {{
		"eth0" : {{
			"name": "eth0",
        "prefix" : "{ip}",
        "gateway": "{gateway}"
		}}
	}}
}}
'''
def getGateway(num):
    fk2=math.floor(fk/2)
    n1=math.floor(num/fk2)
    n2=num%fk2
    podnum=int(n1/fk2)
    inpodnum=n1%fk2
    gw='%s.%s.%s.254'%(podnum+11,inpodnum+11,n2+1)
    return gw

def getIP(num):
    fk2=math.floor(fk/2)
    n1=math.floor(num/fk2)
    n2=num%fk2
    podnum=int(n1/fk2)
    inpodnum=n1%fk2
    ip='%s.%s.%s.1/24'%(podnum+11,inpodnum+11,n2+1)
    return ip



def genbatfish():
    for i in range(0,fk):
        for j in range(0,fk2):
            #sd
            nums=[]
            ethself=[]
            ethother=[]
            for k in range(0,fk2):
                nums.append(i*fk2+fk*fk2+k)
                ethself.append(fk2+k)
                ethother.append(fk2+j)
            writefile(genfbottom(i*fk2+j,nums,ethself,ethother)+
                    genbbottom(i*fk2+j,nums,ethself,ethother)+
                    genzbottom(i*fk2+j,nums,ethself,ethother),"frrR"+str(i*fk2+j)+".conf")
            #su
            nums=[]
            ethself=[]
            ethother=[]
            for k in range(0,fk2):
                nums.append(fk*fk+j*fk2+k)
                ethself.append(k)
                ethother.append(i)
            for k in range(0,fk2):
                nums.append(i*fk2+k)
                ethself.append(k+fk2)
                ethother.append(fk2+j)
            writefile(genfmid(i*fk2+fk*fk2+j,nums,ethself,ethother)+
                    genbmid(i*fk2+fk*fk2+j,nums,ethself,ethother)+
                    genzmid(i*fk2+fk*fk2+j,nums,ethself,ethother),"frrR"+str(i*fk2+fk*fk2+j)+".conf")
    for i in range(0,fk2*fk2):
        #st
        nums=[]
        ethself=[]
        ethother=[]
        tnum=math.floor(i/fk2)
        for k in range(0,fk):
            nums.append(fk*fk2+tnum+k*fk2)
            ethself.append(k)
            ethother.append(i-tnum*fk2)
        writefile(genftop(i+fk*fk,nums,ethself,ethother)+
                genbtop(i+fk*fk,nums,ethself,ethother)+
                genztop(i+fk*fk,nums,ethself,ethother),"frrR"+str(i+fk*fk)+".conf")

    for i in range(0,fk*fk2*fk2):
        data={"name":"h%s"%(i),"ip":getIP(i),"gateway":getGateway(i)}
        writefile(hjs.format(**data),"h%s.json"%(i))

    os.system("mkdir -p configs")
    os.system("mkdir -p hosts")
    #os.system("rm configs/* -r")
    #os.system("rm hosts/* -r")
    for i in range(0,fk*fk+fk2*fk2):
        os.system("cp frrR%s.conf configs/R%s.cfg"%(i,i))
        os.system("rm frrR%s.conf"%(i))
    for i in range(0,fk*fk2*fk2):
        os.system("cp h%s.json hosts/h%s.json"%(i,i))
        os.system("rm h%s.json"%(i))

genbatfish()

tvty='''
service integrated-vtysh-config
hostname R{num}
'''
tdm='''
zebra=yes
bgpd=yes
ospfd=no
ospf6d=no
ripd=no
ripngd=no
isisd=no
pimd=no
pim6d=no
ldpd=no
nhrpd=no
eigrpd=no
babeld=no
sharpd=no
pbrd=no
bfdd=no
fabricd=no
vrrpd=no
pathd=no

vtysh_enable=yes
zebra_options="  -A 127.0.0.1 -s 90000000"
mgmtd_options="  -A 127.0.0.1"
bgpd_options="   -A 127.0.0.1"
ospfd_options="  -A 127.0.0.1"
ospf6d_options=" -A ::1"
ripd_options="   -A 127.0.0.1"
ripngd_options=" -A ::1"
isisd_options="  -A 127.0.0.1"
pimd_options="   -A 127.0.0.1"
pim6d_options="  -A ::1"
ldpd_options="   -A 127.0.0.1"
nhrpd_options="  -A 127.0.0.1"
eigrpd_options=" -A 127.0.0.1"
babeld_options=" -A 127.0.0.1"
sharpd_options=" -A 127.0.0.1"
pbrd_options="   -A 127.0.0.1"
staticd_options="-A 127.0.0.1"
bfdd_options="   -A 127.0.0.1"
fabricd_options="-A 127.0.0.1"
vrrpd_options="  -A 127.0.0.1"
pathd_options="  -A 127.0.0.1"
'''

def genfrr():
    for i in range(0,fk):
        for j in range(0,fk2):
            #sd
            nums=[]
            ethself=[]
            ethother=[]
            for k in range(0,fk2):
                nums.append(i*fk2+fk*fk2+k)
                ethself.append(fk2+k)
                ethother.append(fk2+j)
            writefile(
                    genbbottom(i*fk2+j,nums,ethself,ethother)+
                    genzbottom(i*fk2+j,nums,ethself,ethother),"frrR"+str(i*fk2+j)+".conf")
            #su
            nums=[]
            ethself=[]
            ethother=[]
            for k in range(0,fk2):
                nums.append(fk*fk+j*fk2+k)
                ethself.append(k)
                ethother.append(i)
            for k in range(0,fk2):
                nums.append(i*fk2+k)
                ethself.append(k+fk2)
                ethother.append(fk2+j)
            writefile(
                    genbmid(i*fk2+fk*fk2+j,nums,ethself,ethother)+
                    genzmid(i*fk2+fk*fk2+j,nums,ethself,ethother),"frrR"+str(i*fk2+fk*fk2+j)+".conf")
    for i in range(0,fk2*fk2):
        #st
        nums=[]
        ethself=[]
        ethother=[]
        tnum=math.floor(i/fk2)
        for k in range(0,fk):
            nums.append(fk*fk2+tnum+k*fk2)
            ethself.append(k)
            ethother.append(i-tnum*fk2)
        writefile(
                genbtop(i+fk*fk,nums,ethself,ethother)+
                genztop(i+fk*fk,nums,ethself,ethother),"frrR"+str(i+fk*fk)+".conf")
    for i in range(0,fk*fk+fk2*fk2):
        writefile(tvty.format(num=i),"vtyR%s.conf"%(i))
        writefile(tdm,"dmR%s.conf"%(i))
    for i in range(0,fk*fk+fk2*fk2):
        os.system("mkdir -p /etc/frr/frrR%s"%(i))
        os.system("sudo rm /etc/frr/frrR%s/* -r"%(i))
        os.system("cp frrR%s.conf /etc/frr/frrR%s/frr.conf"%(i,i))
        os.system("cp vtyR%s.conf /etc/frr/frrR%s/vtysh.conf"%(i,i))
        os.system("cp dmR%s.conf /etc/frr/frrR%s/daemons"%(i,i))

#genfrr()