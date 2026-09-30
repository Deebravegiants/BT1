# [?] fix vulnerability: 03 Denial of Service on Payload Length (#111)

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2017-11-23
Source: https://github.com/neo-project/neo/commit/702548f605b44848638a6731ffe5052b8d48e7e5
Type: security-commit

## Details
fix vulnerability: 03 Denial of Service on Payload Length (#111)

## Patch
### neo/Network/Message.cs
```diff
@@ -51,73 +51,89 @@ void ISerializable.Deserialize(BinaryReader reader)
 
         public static async Task<Message> DeserializeFromAsync(Stream stream, CancellationToken cancellationToken)
         {
-            byte[] buffer = new byte[24];
-            await FillBufferAsync(stream, buffer, cancellationToken);
+            uint payload_length;
+            byte[] buffer = await FillBufferAsync(stream, 24, cancellationToken);
             Message message = new Message();
             using (MemoryStream ms = new MemoryStream(buffer, false))
             using (BinaryReader reader = new BinaryReader(ms, Encoding.UTF8))
             {
                 if (reader.ReadUInt32() != Magic)
                     throw new FormatException();
                 message.Command = reader.ReadFixedString(12);
-                uint length = reader.ReadUInt32();
-                if (length > PayloadMaxSize)
+                payload_length = reader.ReadUInt32();
+                if (payload_length > PayloadMaxSize)
                     throw new FormatException();
                 message.Checksum = reader.ReadUInt32();
-                message.Payload = new byte[length];
             }
-            if (message.Payload.Length > 0)
-                await FillBufferAsync(stream, message.Payload, cancellationToken);
+            if (payload_length > 0)
+                message.Payload = await FillBufferAsync(stream, (int)payload_length, cancellationToken);
+            else
+                message.Payload = new byte[0];
             if (GetChecksum(message.Payload) != message.Checksum)
                 throw new FormatException();
             return message;
         }
 
         public static async Task<Message> DeserializeFromAsync(WebSocket socket, CancellationToken cancellationToken)
         {
-            byte[] buffer = new byte[24];
-            await FillBufferAsync(socket, buffer, cancellationToken);
+            uint payload_length;
+            byte[] buffer = await FillBufferAsync(socket, 24, cancellationToken);
             Message message = new Message();
             using (MemoryStream ms = new MemoryStream(buffer, false))
             using (BinaryReader reader = new BinaryReader(ms, Encoding.UTF8))
             {
                 if (reader.ReadUInt32() != Magic)
                     throw new FormatException();
                 message.Command = reader.ReadFixedString(12);
-                uint length = reader.ReadUInt32();
-                if (length > PayloadMaxSize)
+                payload_length = reader.ReadUInt32();
+                if (payload_length > PayloadMaxSize)
                     throw new FormatException();
                 message.Checksum = reader.ReadUInt32();
-                message.Payload = new byte[length];
             }
-            if (message.Payload.Length > 0)
-                await FillBufferAsync(socket, message.Payload, cancellationToken);
+            if (payload_length > 0)
+                message.Payload = await FillBufferAsync(socket, (int)payload_length, cancellationToken);
+            else
+                message.Payload = new byte[0];
             if (GetChecksum(message.Payload) != message.Checksum)
                 throw new FormatException();
             return message;
         }
 
-        private static async Task FillBufferAsync(Stream stream, byte[] buffer, CancellationToken cancellationToken)
+        private static async Task<byte[]> FillBufferAsync(Stream stream, int buffer_size, CancellationToken cancellationToken)
         {
-            int offset = 0;
-            while (offset < buffer.Length)
+            const int MAX_SIZE = 1024;
+            byte[] buffer = new byte[buffer_size < MAX_SIZE ? buffer_size : MAX_SIZE];
+            using (MemoryStream ms = new MemoryStream())
             {
-                int count = await stream.ReadAsync(buffer, offset, buffer.Length - offset, cancellationToken);
-                if (count <= 0) throw new IOException();
-                offset += count;
+                while (buffer_size > 0)
+                {
+                    int count = buffer_size < MAX_SIZE ? buffer_size : MAX_SIZE;
+                    count = await stream.ReadAsync(buffer, 0, count, cancellationToken);
+                    if (count <= 0) throw new IOException();
+                    ms.Write(buffer, 0, count);
+                    buffer_size -= count;
+                }
+                return ms.ToArray();
             }
         }
 
-        private static async Task FillBufferAsync(WebSocket socket, byte[] buffer, CancellationToken cancellationToken)
+        private static async Task<byte[]> FillBufferAsync(WebSocket socket, int buffer_size, CancellationToken cancellationToken)
         {
-            int offset = 0;
-            while (offset < buffer.Length)
+            const int MAX_SIZE = 1024;
+            byte[] buffer = new byte[buffer_size < MAX_SIZE ? buffer_size : MAX_SIZE];
+            using (MemoryStream ms = new MemoryStream())
             {
-                ArraySegment<byte> segment = new ArraySegment<byte>(buffer, offset, buffer.Length - offset);
-                WebSocketReceiveResult result = await socket.ReceiveAsync(segment, cancellationToken);
-                if (result.Count <= 0 || result.MessageType != WebSocketMessageType.Binary)
-                    throw new IOException();
-                offset += result.Count;
+                while (buffer_size > 0)
+                {
+                    int count = buffer_size < MAX_SIZE ? buffer_size : MAX_SIZE;
+                    ArraySegment<byte> segment = new ArraySegment<byte>(buffer, 0, count);
+                    WebSocketReceiveResult result = await socket.ReceiveAsync(segment, cancellationToken);
+                    if (result.Count <= 0 || result.MessageType != WebSocketMessageType.Binary)
+                        throw new IOException();
+                    ms.Write(buffer, 0, result.Count);
+                    buffer_size -= result.Count;
+                }
+                return ms.ToArray();
             }
         }
 
```
