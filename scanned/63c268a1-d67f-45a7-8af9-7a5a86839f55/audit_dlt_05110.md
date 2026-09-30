# [?] seeder: Fix potential UB/race condition when starting DNS threads

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2024-03-19
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/6693b7bfd4a5d64c37415b0bee50c6d8d37b458d
Type: security-commit

## Details
seeder: Fix potential UB/race condition when starting DNS threads

The DNS threads all share a static file descriptor for the listenSocket.
When starting up, the first DNS thread that is created initializes this
socket. However, no locks were being used to ensure that only 1 thread
passes through the initialization at a time.

Instead, the original author of the seeder used a Sleep(20) call to
"hope" that only 1 thread goes through there at once. This is not
guaranteed to always succeed (depending on machine load, scheduler, etc)
and was a potential source of C++ UB.

This commit fixes the situation by ensuring no such race can occur at
app startup, thus ensuring no UB.

## Patch
### src/seeder/dns.cpp
```diff
@@ -3,6 +3,7 @@
 // file COPYING or http://www.opensource.org/licenses/mit-license.php.
 
 #include <seeder/dns.h>
+#include <sync.h>
 
 #include <arpa/inet.h>
 #include <netinet/in.h>
@@ -585,7 +586,15 @@ ssize_t DnsServer::handle(const uint8_t *inbuf, size_t insize, uint8_t *outbuf)
     return 12;
 }
 
-static int listenSocket = -1;
+static SharedMutex listenSocketMut;
+static int listenSocket GUARDED_BY(listenSocketMut) = -1;
+
+static void closeSocket_nolock() EXCLUSIVE_LOCKS_REQUIRED(listenSocketMut) {
+    if (listenSocket > -1) {
+        close(listenSocket);
+    }
+    listenSocket = -1;
+}
 
 DnsServer::DnsServer(int port_, const char *host_, const char *ns_, const char *mbox_, int datattl_, int nsttl_)
     : port(port_), datattl(datattl_), nsttl(nsttl_), host(host_), ns(ns_), mbox(mbox_) {}
@@ -601,26 +610,28 @@ int DnsServer::run() {
     }
 
     int replySocket;
-    if (listenSocket == -1) {
-        struct sockaddr_in6 si_me;
-        if ((listenSocket = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
-            return -1;
-        }
-        replySocket = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDP);
-        if (replySocket == -1) {
-            close(listenSocket);
-            return -1;
-        }
-        int sockopt = 1;
-        setsockopt(listenSocket, IPPROTO_IPV6, DSTADDR_SOCKOPT, &sockopt,
-                   sizeof sockopt);
-        std::memset((char *)&si_me, 0, sizeof(si_me));
-        si_me.sin6_family = AF_INET6;
-        si_me.sin6_port = htons(this->port);
-        si_me.sin6_addr = in6addr_any;
-        if (bind(listenSocket, (struct sockaddr *)&si_me, sizeof(si_me)) ==
-            -1) {
-            return -2;
+    {
+        LOCK(listenSocketMut);
+        if (listenSocket == -1) {
+            struct sockaddr_in6 si_me;
+            if ((listenSocket = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
+                return -1;
+            }
+            replySocket = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDP);
+            if (replySocket == -1) {
+                closeSocket_nolock();
+                return -1;
+            }
+            const int sockopt = 1;
+            setsockopt(listenSocket, IPPROTO_IPV6, DSTADDR_SOCKOPT, &sockopt, sizeof sockopt);
+            std::memset((char *)&si_me, 0, sizeof(si_me));
+            si_me.sin6_family = AF_INET6;
+            si_me.sin6_port = htons(this->port);
+            si_me.sin6_addr = in6addr_any;
+            if (bind(listenSocket, (struct sockaddr *)&si_me, sizeof(si_me)) == -1) {
+                closeSocket_nolock();
+                return -2;
+            }
         }
     }
 
@@ -634,7 +645,7 @@ int DnsServer::run() {
     };
 
     union control_data cmsg;
-    msghdr msg;
+    msghdr msg = {};
     msg.msg_name = &si_other;
     msg.msg_namelen = sizeof(si_other);
     msg.msg_iov = iov;
@@ -643,6 +654,7 @@ int DnsServer::run() {
     msg.msg_controllen = sizeof(cmsg);
 
     for (; 1; ++this->nRequests) {
+        LOCK_SHARED(listenSocketMut);
         ssize_t insize = recvmsg(listenSocket, &msg, 0);
         //    uint8_t *addr = (uint8_t*)&si_other.sin_addr.s_addr;
         //    std::fprintf(stdout, "DNS: Request %llu from %i.%i.%i.%i:%i of %i
```

### src/seeder/main.cpp
```diff
@@ -575,7 +575,6 @@ int main(int argc, char **argv) {
             dnsThreads.push_back(new CDnsThread(&opts, i));
             pthread_create(&threadDns, nullptr, ThreadDNS, dnsThreads.back());
             std::fprintf(stdout, ".");
-            Sleep(20);
         }
         std::fprintf(stdout, "done\n");
     }
```
