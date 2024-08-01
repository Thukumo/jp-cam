import requests, ipaddress

def isvailed(s):
    try:
        #return ipaddress.ip_address(s).version == 4
        ipaddress.IPv4Network(s)
        return True
    except Exception:
        return False

def b(url):
    return [[ip.split("/")[0], str(ipaddress.IPv4Address(ip.split("/")[0])+ipaddress.IPv4Network(ip).num_addresses)] for ip in [c.strip() for c in requests.get(url, headers={"User-Agent": "testBot"}).text.split("\n") if isvailed(c.strip())]]

code_str = "using System.Net;\n\
namespace jp_cam\n\
{\n\
    internal class Tools\n\
    {\n"

li = []
lis_alphabet = "abcdefghijklmnopqrstuvwxyz"
b("https://ipv4.fetus.jp/jp.txt")
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
