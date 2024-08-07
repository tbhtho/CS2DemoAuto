using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using GameOverlay.Drawing;
using GameOverlay.Windows;

namespace cs2overlay
{
    class Program
    {
        private static Graphics _graphics;
        private static StickyWindow _window;
        private static List<string> _commands = new List<string>();
        private static readonly object _lock = new object();

        static void Main(string[] args)
        {
            var process = Process.GetProcessesByName("cs2"); // Use the correct process name for CS2
            if (process.Length == 0)
            {
                Console.WriteLine("CS2 is not running.");
                return;
            }

            IntPtr handle = process[0].MainWindowHandle;

            _graphics = new Graphics()
            {
                MeasureFPS = true,
                PerPrimitiveAntiAliasing = true,
                TextAntiAliasing = true
            };

            _window = new StickyWindow(handle, _graphics)
            {
                FPS = 600,
                IsTopmost = true,
                IsVisible = true
            };

            _window.SetupGraphics += SetupGraphics;
            _window.DrawGraphics += DrawGraphics;

            _window.Create();

            // Start a new thread for listening to TCP commands
            Thread tcpListenerThread = new Thread(new ThreadStart(StartTcpListener));
            tcpListenerThread.Start();

            Console.WriteLine("Overlay running. Press Enter to exit...");
            Console.ReadLine();

            _window.Dispose();
            _graphics.Dispose();
        }

        private static void SetupGraphics(object sender, SetupGraphicsEventArgs e)
        {
            var gfx = e.Graphics;
            gfx.BeginScene(); // Begin the scene
            gfx.ClearScene(Color.Transparent);
            gfx.EndScene(); // End the scene
        }

        private static void DrawGraphics(object sender, DrawGraphicsEventArgs e)
        {
            var gfx = e.Graphics;

            gfx.BeginScene(); // Begin the scene
            gfx.ClearScene(Color.Transparent);

            // Draw text on the overlay
            using (var font = gfx.CreateFont("Arial", 14))
            using (var brush = gfx.CreateSolidBrush(255, 255, 255))
            {
                gfx.DrawText(font, brush, 100, 100, "Cs2 Demo automation");

                lock (_lock)
                {
                    int y = 150;
                    foreach (var command in _commands)
                    {
                        gfx.DrawText(font, brush, 100, y, command);
                        y += 20; // Adjust the spacing between lines
                    }
                }
            }

            gfx.EndScene(); // End the scene
        }

        private static void StartTcpListener()
        {
            TcpListener server = new TcpListener(IPAddress.Parse("127.0.0.1"), 5000);
            server.Start();
            Console.WriteLine("[auto] TCP Server started, waiting for connection...");

            while (true)
            {
                TcpClient client = server.AcceptTcpClient();
                NetworkStream stream = client.GetStream();
                byte[] buffer = new byte[client.ReceiveBufferSize];
                int bytesRead = stream.Read(buffer, 0, client.ReceiveBufferSize);
                string command = Encoding.ASCII.GetString(buffer, 0, bytesRead);

                Console.WriteLine($"[auto] Received command: {command}");
                Console.WriteLine($"[auto] Succesfully Done");
                lock (_lock)
                {
                    _commands.Add(command);
                    if (_commands.Count > 10) // Limit the number of commands displayed
                    {
                        _commands.RemoveAt(0);
                    }
                }

                client.Close();
            }
        }
    }
}
