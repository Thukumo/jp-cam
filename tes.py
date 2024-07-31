import requests, ipaddress
from bs4 import BeautifulSoup

def isvailed(s):
    try:
        return ipaddress.ip_address(s).version == 4
    except Exception:
        return False
def a(url):
    tmp = [c.strip() for c in BeautifulSoup(requests.get(url).text, "html.parser").select_one("#primaryContent > table").text.split("\n") if isvailed(c.strip())]
    lis = []
    if len(tmp)%2 != 0:
        print("Error")
        exit()
    for i in range(0, len(tmp), 2):
        lis.append([tmp[i], tmp[i+1]])
    return lis

code_str = "using System.Net;\n\
namespace jp_cam\n\
{\n\
    internal class Tools\n\
    {\n\
        public static bool IsIpBetween(string ip1, string ip2, uint ntargetIp)\n\
        {\n\
            byte[] bip1 = IPAddress.Parse(ip1).GetAddressBytes();\n\
            Array.Reverse(bip1);\n\
            uint nip1 = BitConverter.ToUInt32(bip1, 0);\n\
            byte[] bip2 = IPAddress.Parse(ip2).GetAddressBytes();\n\
            Array.Reverse(bip2);\n\
            uint nip2 = BitConverter.ToUInt32(bip2, 0);\n\
            return nip1 <= ntargetIp && ntargetIp <= nip2;\n\
        }\n\
        public static bool IsJapaneseIP(string ip_str)\n\
        {\n"
li = a("https://www.nic.ad.jp/ja/dns/jp-addr-block.html") + a("https://www.nic.ad.jp/ja/dns/ap-addr-block.html")
if len(li) == 0: exit()
code_str += "            byte[] ip_b = IPAddress.Parse(ip_str).GetAddressBytes();\n"
code_str += "            Array.Reverse(ip_b);\n"
code_str += "            uint ip_num = BitConverter.ToUInt32(ip_b, 0);\n"
code_str += f'            return IsIpBetween("{li[0][0]}", "{li[0][1]}", ip_num)'
li.remove(li[0])
for l in li:
    code_str += f' || IsIpBetween("{l[0]}", "{l[1]}", ip_num)'
code_str += ";\n"
code_str += "\
        }\n\
    }\n\
}\n"
print(code_str)
with open("jpip.cs", "w", encoding="UTF-8") as f:
    f.write(code_str)
print("len: "+str(len(li)))
