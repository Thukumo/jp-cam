using System.Net.Sockets;
using System.Text;

namespace jp_cam
{
    internal class Program
    {
        public static async Task<string> IsConnectableAsync(string ip, int port, int timeout, bool tcp, bool ignore_err)
        {
            Socket? socket = null;
            try
            {
                socket = new(SocketType.Stream, ProtocolType.Tcp){Blocking = false};
                socket.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
                return await Task.WhenAny(Task.Run(async () => 
                {
                    try
                    {
                        if(await Task.WhenAny(Task.Run(async () =>  {
                            await socket.ConnectAsync(ip, port);
                            return false;
                        }), Task.Run(async () => {
                            await Task.Delay(timeout*500+1000);
                            return true;
                        })).Result) return false; //ここ(34～40行目)想定通りの動作してなさそう なんか考える
                        if(!tcp)
                        {
                            await socket.SendAsync(Encoding.ASCII.GetBytes("GET / HTTP/1.1\r\nHost: " + ip + "\r\nConnection: close\r\n\r\n"), SocketFlags.None);
                            byte[] buffer = new byte[1024];
                            await socket.ReceiveAsync(buffer, SocketFlags.None);
                            //Console.WriteLine(ip+" "+Encoding.ASCII.GetString(buffer).Split(' ')[1]);
                            if(ignore_err) return !Encoding.ASCII.GetString(buffer).Split(' ')[1].StartsWith("404"); //403も弾いていいかな?
                        }
                        return true;
                    }
                    catch(Exception ex) when (ex is SocketException || ex is TaskCanceledException || ex is ObjectDisposedException)
                    {
                        return false;
                    }
                }), Task.Run(async () => 
                {
                    await Task.Delay(timeout*1000);
                    return false;
                })).Result? ip : "";
            }
            catch(Exception ex) when (ex is SocketException || ex is TaskCanceledException || ex is ObjectDisposedException)
            {
                return "";
            }
            finally
            {
                socket?.Close();
            }
        }
        public static void Main(string[] args)
        {
            int port = 80, timeout = 30;
            bool tcp = false, memo = false, ignore_err = false;
            for(int i = 0; i < args.Length; i++)
            {
                tcp |= "TCP".Equals(args[i], StringComparison.OrdinalIgnoreCase);
                ignore_err |= "IGNORE".Equals(args[i], StringComparison.OrdinalIgnoreCase) || "IG".Equals(args[i], StringComparison.OrdinalIgnoreCase);
                if (("TIMEOUT".Equals(args[i], StringComparison.OrdinalIgnoreCase) || "TO".Equals(args[i], StringComparison.OrdinalIgnoreCase)) && i + 1 < args.Length) if(memo = int.TryParse(args[i+1], out int tmp)) timeout = tmp;
                else
                {
                    if(memo) memo = false;
                    else if(int.TryParse(args[i], out tmp)) port = tmp;
                }
            }
            Console.Error.WriteLine("Port: " + port);
            Console.Error.WriteLine("Timeout: " + timeout);
            Console.Error.WriteLine("Protocol: " + (tcp? "TCP": "HTTP"));
            Console.Error.WriteLine("Ignore Error: " + ignore_err);
            Random random = new();
            string country = "jp";
            Parallel.ForEach(Tools.addr_blocks[country].OrderBy(x => random.Next()), (i) =>
            {
                List<Task<string>> tasks = [];
                for(uint j = 0; j < (i.End-i.Start)/256; j++)
                {
                    for(uint k = 0; k < 256; k++) tasks.Add(IsConnectableAsync(Tools.UIntToIp(i.Start+256*j+k).ToString(), port, timeout, tcp, ignore_err));
                    Task.WhenAll(tasks).Wait();
                    foreach(Task<string> task in tasks) if(task.Result != "")
                    {
                        Console.WriteLine(task.Result);
                        Console.Error.WriteLine(task.Result);
                    }
                    tasks.Clear();
                }
                for(uint j = 0; j < (i.End-i.Start)%256; j++)
                {
                    tasks.Add(IsConnectableAsync(Tools.UIntToIp(i.End-(i.End-i.Start)%256+j).ToString(), port, timeout, tcp, ignore_err));
                    Task.WhenAll(tasks).Wait();
                    foreach(Task<string> task in tasks) if(task.Result != "")
                    {
                        Console.WriteLine(task.Result);
                        Console.Error.WriteLine(task.Result);
                    }
                    tasks.Clear();
                }
            });
            Console.Error.WriteLine("探索が終了しました。");
        }
    }
}
