# [?] Fix Windows crash at startup introduced by MR !786

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2020-10-15
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/1fc367e5dc1290c2615b2f73e89c96925668fa3a
Type: security-commit

## Details
Fix Windows crash at startup introduced by MR !786

Summary
---

MR !786 introduced a hard crash at startup for Windows because it
relied on the gethostaddr() facility which, on Windows, is not available
at all until after WSAStartup() is called.

The crash produced the following error when running on a real Windows
system (not WINE), and it was due to the fact that we are now doing
LookupName() which calls getaddrinfo() in winsock before WSAStartup()
was called.  Here is the error:

```
D:\bchn>bin\bitcoind.exe -hh
terminate called after throwing an instance of 'std::invalid_argument'
  what():  Unable to parse numeric-IP:port pair: 2.37.183.149:8333
This application has requested the Runtime to terminate it in an unusual way.
Please contact the application's support team for more information.
```

Since we only ever call WSAStartup() once in this codebase, and always with
the same exact 2,2 WSA version request, it is safe to call this at any time.

Calling it earlier or later has no negative effect -- all of the other
things this codebase does on Windows has no effect on this DLL's
initialization.

The reason this restriction exists in Windows is so that the same DLL
can support multiple "personalities" or APIs depending on the version
requested at runtime by the application.

On every other platform no such restriction exists.  WSAStartup() is
used by applications to declare the version of the winsock API they want to use.

Test Plan
---

1. Build bitcoind without this commit, run it on a real Windows system
   (not Wine), verify that it crashes on startup `bitcoind -hh` should fail.
2. Build bitcoind with this commit, verify that it does not crash and
   executes normally.

Bonus: Start an IBD on Windows just to test out networking.

## Patch
### src/netbase.cpp
```diff
@@ -79,6 +79,16 @@ static bool LookupIntern(const char *pszName, std::vector<CNetAddr> &vIP,
             return true;
         }
     }
+#ifdef WIN32
+    // Windows: WSAStartup must be called before getaddrinfo below will work.
+    // SetupNetworking() is a no-op on all platforms except Windows, and on
+    // Windows it is guaranteed to be ok to call more than once in this
+    // codebase. This was added after MR !786, which ends up calling into here
+    // during static initialization, before SetupNetworking() could be called
+    // by init.cpp.
+    static const bool setupOnce = SetupNetworking(); // leverage C++ guarantee this is called just once.
+    (void)setupOnce;
+#endif
 
     struct addrinfo aiHint;
     memset(&aiHint, 0, sizeof(struct addrinfo));
```

### src/util/system.cpp
```diff
@@ -1395,15 +1395,23 @@ void SetupEnvironment() {
 
 bool SetupNetworking() {
 #ifdef WIN32
-    // Initialize Windows Sockets.
-    WSADATA wsadata;
-    int ret = WSAStartup(MAKEWORD(2, 2), &wsadata);
-    if (ret != NO_ERROR || LOBYTE(wsadata.wVersion) != 2 ||
-        HIBYTE(wsadata.wVersion) != 2) {
-        return false;
-    }
-#endif
+    // the below guard is to ensure we can call SetupNetworking() from multiple
+    // places in the codebase and that WSAStartup() will only execute precisely
+    // once, with the results cached in the static variable.
+    static const bool wsaResult = [] {
+        // Initialize Windows Sockets.
+        WSADATA wsadata;
+        int ret = WSAStartup(MAKEWORD(2, 2), &wsadata);
+        if (ret != NO_ERROR || LOBYTE(wsadata.wVersion) != 2 ||
+            HIBYTE(wsadata.wVersion) != 2) {
+            return false;
+        }
+        return true;
+    }();
+    return wsaResult;
+#else
     return true;
+#endif
 }
 
 int GetNumCores() {
```
