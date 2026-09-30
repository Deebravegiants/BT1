# [?] Fix Denial of Service with bad UPnP responses (#387)

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2018-09-20
Source: https://github.com/neo-project/neo/commit/515c3ef3ff1f3f9c565331fb0a50cca26b61cab1
Type: security-commit

## Details
Fix Denial of Service with bad UPnP responses (#387)

## Patch
### neo/Network/UPnP.cs
```diff
@@ -34,28 +34,32 @@ public static bool Discover()
             s.SendTo(data, ipe);
 
             byte[] buffer = new byte[0x1000];
+            
             do
             {
                 int length;
                 try
                 {
                     length = s.Receive(buffer);
+
+                    string resp = Encoding.ASCII.GetString(buffer, 0, length).ToLower();
+                    if (resp.Contains("upnp:rootdevice"))
+                    {
+                        resp = resp.Substring(resp.ToLower().IndexOf("location:") + 9);
+                        resp = resp.Substring(0, resp.IndexOf("\r")).Trim();
+                        if (!string.IsNullOrEmpty(_serviceUrl = GetServiceUrl(resp)))
+                        {
+                            return true;
+                        }
+                    }
                 }
-                catch (SocketException)
+                catch
                 {
                     continue;
                 }
-                string resp = Encoding.ASCII.GetString(buffer, 0, length).ToLower();
-                if (resp.Contains("upnp:rootdevice"))
-                {
-                    resp = resp.Substring(resp.ToLower().IndexOf("location:") + 9);
-                    resp = resp.Substring(0, resp.IndexOf("\r")).Trim();
-                    if (!string.IsNullOrEmpty(_serviceUrl = GetServiceUrl(resp)))
-                    {
-                        return true;
-                    }
-                }
-            } while (DateTime.Now - start < TimeOut);
+            }
+            while (DateTime.Now - start < TimeOut);
+
             return false;
         }
 
```
