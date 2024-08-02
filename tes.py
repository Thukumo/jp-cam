import requests, ipaddress

def isvailed(s):
    try:
        ipaddress.IPv4Network(s)
        return True
    except Exception:
        return False

code_str = "using System.Net;\n\
namespace jp_cam\n\
{\n\
    internal class Tools\n\
    {\n\
        public static readonly Dictionary<string, (uint Start, uint End)[]> addr_blocks = new()\n\
        {\n"
countrys = list(map(lambda x: x.lower(), ["jp"])) #えらいので入力の正規化
for country in countrys:
    li = [[ip.split("/")[0], str(ipaddress.IPv4Address(ip.split("/")[0])+ipaddress.IPv4Network(ip).num_addresses)] for ip in [c.strip() for c in requests.get(f"https://ipv4.fetus.jp/{country}.txt", headers={"User-Agent": "testBot"}).text.split("\n") if isvailed(c.strip())]]
    if len(li) == 0: continue
    code_str += "            {\""+country+"\", \n"
    code_str += "            new (uint, uint)[]{\n"
    code_str += f'                (IpSToUInt("{li[0][0]}"), IpSToUInt("{li[0][1]}"))'
    li.remove(li[0])
    for l in li:
        code_str += ",\n"
        code_str += f'                (IpSToUInt("{l[0]}"), IpSToUInt("{l[1]}"))'
    code_str += "\n\
                }\n\
            }\n"
code_str += "\
        };\n\
        public static uint IpSToUInt(string ip)\n\
        {\n\
            byte[] bip = IPAddress.Parse(ip).GetAddressBytes();\n\
            Array.Reverse(bip);\n\
            return BitConverter.ToUInt32(bip, 0);\n\
        }\n\
        public static IPAddress UIntToIp(uint ip)\n\
        {\n\
            byte[] bytes = BitConverter.GetBytes(ip);\n\
            Array.Reverse(bytes);\n\
            return new IPAddress(bytes);\n\
        }\n\
        public static bool IsIpInCountry(string ip_str, string country)\n\
        {\n\
            uint ip_num = IpSToUInt(ip_str);\n\
            foreach (var (Start, End) in addr_blocks[country]) if(Start <= ip_num && ip_num <= End) return true;\n\
            return false;\n\
        }\n\
    }\n\
}\n"
with open("tools.cs", "w", encoding="UTF-8") as f:
    f.write(code_str)
print("len: "+str(len(li)))
