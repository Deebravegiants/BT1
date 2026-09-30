# [?] prevent crash from xunlei;

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2016-08-11
Source: https://github.com/neo-project/neo/commit/ab8befc3bf3506bb44f57fa45b87285cdb94bb4f
Type: security-commit

## Details
prevent crash from xunlei;

## Patch
### AntSharesCore/Network/RemoteNode.cs
```diff
@@ -66,13 +66,13 @@ internal async Task ConnectAsync()
             try
             {
                 await tcp.ConnectAsync(address, ListenerEndpoint.Port);
+                OnConnected();
             }
             catch (SocketException)
             {
                 Disconnect(false);
                 return;
             }
-            OnConnected();
             StartProtocol();
         }
 
```
