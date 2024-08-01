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
    {\n"
li = a("https://www.nic.ad.jp/ja/dns/jp-addr-block.html") + a("https://www.nic.ad.jp/ja/dns/ap-addr-block.html")
if len(li) == 0: exit()
code_str += f"        public static (uint Start, uint End)[] jp_addr_block = \n"
code_str += "        [\n"
code_str += f'            (ToUInt("{li[0][0]}"), ToUInt("{li[0][1]}"))'
li.remove(li[0])
for l in li:
    code_str += ",\n"
    code_str += f'            (ToUInt("{l[0]}"), ToUInt("{l[1]}"))'
code_str += "\n\
        ];\n\
        public static uint ToUInt(string ip)\n\
        {\n\
            byte[] bip = IPAddress.Parse(ip).GetAddressBytes();\n\
            Array.Reverse(bip);\n\
            return BitConverter.ToUInt32(bip, 0);\n\
        }\n\
        public static bool IsJapaneseIP(string ip_str)\n\
        {\n\
            uint ip_num = ToUInt(ip_str);\n\
            foreach (var (Start, End) in jp_addr_block) if(Start <= ip_num && ip_num <= End) return true;\n\
            return false;\n\
        }\n\
    }\n\
}\n"
#print(code_str)
with open("tools.cs", "w", encoding="UTF-8") as f:
    f.write(code_str)
print("len: "+str(len(li)))
