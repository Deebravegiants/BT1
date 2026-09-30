# [?] Fix libevent bufferevent write deadlock

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2021-02-05
Source: https://github.com/Zilliqa/zq1/commit/9b50a2ca8fe519b1e877f05d0e8ce950e017594c
Type: security-commit

## Details
Fix libevent bufferevent write deadlock

## Patch
### src/depends/Schnorr
```diff
@@ -1 +1 @@
-Subproject commit 2ac5a182b92b6a2f756704c6ec3b2cd1a5fd548a
+Subproject commit fae3f4b8dee4d31c1e9683b234972c15ce544c42
```

### src/libNetwork/P2PComm.cpp
```diff
@@ -531,7 +531,7 @@ void P2PComm::CloseAndFreeBufferEvent(struct bufferevent* bufev) {
   bufferevent_free(bufev);
 }
 
-void P2PComm::CloseAndFreeBevP2PSeedConn(struct bufferevent* bufev) {
+void P2PComm::CloseAndFreeBevP2PSeedConnServer(struct bufferevent* bufev) {
   lock(m_mutexPeerConnectionCount, m_mutexBufferEvent);
   unique_lock<mutex> lock(m_mutexPeerConnectionCount, adopt_lock);
   lock_guard<mutex> g(m_mutexBufferEvent, adopt_lock);
@@ -542,7 +542,7 @@ void P2PComm::CloseAndFreeBevP2PSeedConn(struct bufferevent* bufev) {
   char* strAdd = inet_ntoa(cli_addr.sin_addr);
   int port = cli_addr.sin_port;
   // TODO Remove log
-  LOG_GENERAL(DEBUG, "P2PSeed CloseAndFreeBevP2PSeedConn ip="
+  LOG_GENERAL(DEBUG, "P2PSeed CloseAndFreeBevP2PSeedConnServer ip="
                          << strAdd << " port=" << port << " bev=" << bufev);
   uint128_t ipAddr = cli_addr.sin_addr.s_addr;
   {
@@ -558,6 +558,41 @@ void P2PComm::CloseAndFreeBevP2PSeedConn(struct bufferevent* bufev) {
   bufferevent_free(bufev);
 }
 
+void P2PComm::CloseAndFreeBevP2PSeedConnClient(struct bufferevent* bufev,
+                                               void* ctx) {
+  lock(m_mutexPeerConnectionCount, m_mutexBufferEvent);
+  unique_lock<mutex> lock(m_mutexPeerConnectionCount, adopt_lock);
+  lock_guard<mutex> g(m_mutexBufferEvent, adopt_lock);
+  int fd = bufferevent_getfd(bufev);
+  struct sockaddr_in cli_addr {};
+  socklen_t addr_size = sizeof(struct sockaddr_in);
+  getpeername(fd, (struct sockaddr*)&cli_addr, &addr_size);
+  char* strAdd = inet_ntoa(cli_addr.sin_addr);
+  int port = cli_addr.sin_port;
+  // TODO Remove log
+  LOG_GENERAL(DEBUG, "P2PSeed CloseAndFreeBevP2PSeedConnClient ip="
+                         << strAdd << " port=" << port << " bev=" << bufev);
+  uint128_t ipAddr = cli_addr.sin_addr.s_addr;
+  {
+    if (m_peerConnectionCount[ipAddr] > 0) {
+      m_peerConnectionCount[ipAddr]--;
+      // TODO Remove log
+      LOG_GENERAL(DEBUG, "P2PSeed decrementing connection count for ipaddr="
+                             << ipAddr << " m_peerConnectionCount="
+                             << m_peerConnectionCount[ipAddr]);
+    }
+  }
+  // free request msg memory
+  bytes* destBytes = (bytes*)ctx;
+  if (destBytes != NULL) {
+    LOG_GENERAL(DEBUG, "P2PSeed Deleting ctx len=" << destBytes->size());
+    delete destBytes;
+    destBytes = NULL;
+  }
+  bufferevent_setcb(bufev, NULL, NULL, NULL, NULL);
+  bufferevent_free(bufev);
+}
+
 void P2PComm::ClearPeerConnectionCount() {
   std::unique_lock<std::mutex> lock(m_mutexPeerConnectionCount);
   m_peerConnectionCount.clear();
@@ -765,7 +800,7 @@ void P2PComm::EventCbServerSeed(struct bufferevent* bev, short events,
   }
   if (events & (BEV_EVENT_EOF | BEV_EVENT_ERROR)) {
     RemoveBevFromMap(peer);
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
   }
 }
 
@@ -803,13 +838,13 @@ void P2PComm::ReadCbServerSeed(struct bufferevent* bev,
   struct evbuffer* input = bufferevent_get_input(bev);
   if (input == NULL) {
     LOG_GENERAL(WARNING, "Error: bufferevent_get_input failure.");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
     return;
   }
   size_t len = evbuffer_get_length(input);
   if (len == 0) {
     LOG_GENERAL(WARNING, "Error: evbuffer_get_length failure.");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
     return;
   }
   if (len >= MAX_READ_WATERMARK_IN_BYTES) {
@@ -819,20 +854,20 @@ void P2PComm::ReadCbServerSeed(struct bufferevent* bev,
                              << from.GetPrintableIPAddress()
                              << " as strictly blacklisted");
     Blacklist::GetInstance().Add(from.m_ipAddress);
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
   }
 
   bytes message(len);
   if (evbuffer_copyout(input, message.data(), len) !=
       static_cast<ev_ssize_t>(len)) {
     LOG_GENERAL(WARNING, "Error: evbuffer_copyout failure.");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
     return;
   }
 
   if (message.size() <= HDR_LEN) {
     LOG_GENERAL(WARNING, "Error: Empty message received.");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
     return;
   }
 
@@ -843,7 +878,7 @@ void P2PComm::ReadCbServerSeed(struct bufferevent* bev,
     LOG_GENERAL(WARNING, "Header version wrong, received ["
                              << version - 0x00 << "] while expected ["
                              << MSG_VERSION << "].");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
     return;
   }
 
@@ -852,7 +887,7 @@ void P2PComm::ReadCbServerSeed(struct bufferevent* bev,
     LOG_GENERAL(WARNING, "Header chainid wrong, received ["
                              << chainId << "] while expected [" << CHAIN_ID
                              << "].");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
     return;
   }
 
@@ -865,14 +900,14 @@ void P2PComm::ReadCbServerSeed(struct bufferevent* bev,
 
     if (!SafeMath<uint32_t>::sub(message.size(), HDR_LEN, res)) {
       LOG_GENERAL(WARNING, "Error: Unexpected subtraction operation!");
-      CloseAndFreeBevP2PSeedConn(bev);
+      CloseAndFreeBevP2PSeedConnServer(bev);
       return;
     }
 
     if (res > messageLength) {
       LOG_GENERAL(WARNING,
                   "Error: Received msg len is greater than header msg len")
-      CloseAndFreeBevP2PSeedConn(bev);
+      CloseAndFreeBevP2PSeedConnServer(bev);
       return;
     } else if (res < messageLength) {
       return;
@@ -881,7 +916,7 @@ void P2PComm::ReadCbServerSeed(struct bufferevent* bev,
 
   if (evbuffer_drain(input, len) != 0) {
     LOG_GENERAL(WARNING, "Error: evbuffer_drain failure.");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
     return;
   }
 
@@ -910,7 +945,7 @@ void P2PComm::ReadCbServerSeed(struct bufferevent* bev,
   } else {
     // Unexpected start byte. Drop this message
     LOG_CHECK_FAIL("Start byte", startByte, START_BYTE_SEED_TO_SEED_REQUEST);
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnServer(bev);
   }
 }
 
@@ -995,19 +1030,17 @@ void P2PComm::RemoveBevFromMap(const Peer& peer) {
 }
 
 void P2PComm ::EventCbClientSeed([[gnu::unused]] struct bufferevent* bev,
-                                 short events, [[gnu::unused]] void* ctx) {
+                                 short events, void* ctx) {
   int fd = bufferevent_getfd(bev);
   struct sockaddr_in cli_addr {};
   socklen_t addr_size = sizeof(struct sockaddr_in);
   getpeername(fd, (struct sockaddr*)&cli_addr, &addr_size);
   Peer peer(cli_addr.sin_addr.s_addr, cli_addr.sin_port);
+  bytes* destBytes = (bytes*)ctx;
   LOG_GENERAL(DEBUG, "P2PSeed EventCbClient peer=" << peer << " bev=" << bev);
   // TODO Remove all if conditions except last two. For now debugging purpose
   // only
   if (DEBUG_LEVEL == 4) {
-    if (events & BEV_EVENT_CONNECTED) {
-      LOG_GENERAL(DEBUG, "P2PSeed BEV_EVENT_CONNECTED");
-    }
     if (events & BEV_EVENT_ERROR) {
       LOG_GENERAL(WARNING, "Error: P2PSeed BEV_EVENT_ERROR");
     }
@@ -1020,19 +1053,32 @@ void P2PComm ::EventCbClientSeed([[gnu::unused]] struct bufferevent* bev,
     if (events & BEV_EVENT_EOF) {
       LOG_GENERAL(DEBUG, "P2PSeed BEV_EVENT_EOF");
     }
+    if (events & BEV_EVENT_TIMEOUT) {
+      LOG_GENERAL(DEBUG, "P2PSeed BEV_EVENT_TIMEOUT");
+    }
+    if (events & BEV_EVENT_CONNECTED) {
+      LOG_GENERAL(DEBUG, "P2PSeed BEV_EVENT_CONNECTED req msg len="
+                             << destBytes->size());
+    }
+  }
+  if (events & BEV_EVENT_CONNECTED) {
+    if (destBytes != NULL) {
+      if (bufferevent_write(bev, &(destBytes->at(0)), destBytes->size()) < 0) {
+        LOG_GENERAL(WARNING, "Error: P2PSeed bufferevent_write failed !!!");
+        return;
+      }
+    }
   }
   if (events & (BEV_EVENT_EOF | BEV_EVENT_ERROR)) {
     bufferevent_set_timeouts(bev, NULL, NULL);
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
   }
   if (events & BEV_EVENT_TIMEOUT) {
-    LOG_GENERAL(DEBUG, "P2PSeed BEV_EVENT_TIMEOUT");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
   }
 }
 
-void P2PComm ::ReadCbClientSeed(struct bufferevent* bev,
-                                [[gnu::unused]] void* ctx) {
+void P2PComm ::ReadCbClientSeed(struct bufferevent* bev, void* ctx) {
   int fd = bufferevent_getfd(bev);
   struct sockaddr_in cli_addr {};
   socklen_t addr_size = sizeof(struct sockaddr_in);
@@ -1043,13 +1089,13 @@ void P2PComm ::ReadCbClientSeed(struct bufferevent* bev,
   struct evbuffer* input = bufferevent_get_input(bev);
   if (input == NULL) {
     LOG_GENERAL(WARNING, "Error: bufferevent_get_input failure.");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
     return;
   }
   size_t len = evbuffer_get_length(input);
   if (len == 0) {
     LOG_GENERAL(WARNING, "Error: evbuffer_get_length failure.");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
     return;
   }
   if (len >= MAX_READ_WATERMARK_IN_BYTES) {
@@ -1059,20 +1105,20 @@ void P2PComm ::ReadCbClientSeed(struct bufferevent* bev,
                              << from.GetPrintableIPAddress()
                              << " as strictly blacklisted");
     Blacklist::GetInstance().Add(from.m_ipAddress);
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
   }
 
   bytes message(len);
   if (evbuffer_copyout(input, message.data(), len) !=
       static_cast<ev_ssize_t>(len)) {
     LOG_GENERAL(WARNING, "Error: evbuffer_copyout failure.");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
     return;
   }
 
   if (message.size() <= HDR_LEN) {
     LOG_GENERAL(WARNING, "Error: Empty message received.");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
     return;
   }
 
@@ -1083,7 +1129,7 @@ void P2PComm ::ReadCbClientSeed(struct bufferevent* bev,
     LOG_GENERAL(WARNING, "Header version wrong, received ["
                              << version - 0x00 << "] while expected ["
                              << MSG_VERSION << "].");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
     return;
   }
 
@@ -1092,7 +1138,7 @@ void P2PComm ::ReadCbClientSeed(struct bufferevent* bev,
     LOG_GENERAL(WARNING, "Header chainid wrong, received ["
                              << chainId << "] while expected [" << CHAIN_ID
                              << "].");
-    CloseAndFreeBevP2PSeedConn(bev);
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
     return;
   }
 
@@ -1105,25 +1151,23 @@ void P2PComm ::ReadCbClientSeed(struct bufferevent* bev,
 
     if (!SafeMath<uint32_t>::sub(message.size(), HDR_LEN, res)) {
       LOG_GENERAL(WARNING, "Error: Unexpected subtraction operation!");
-      CloseAndFreeBevP2PSeedConn(bev);
+      CloseAndFreeBevP2PSeedConnClient(bev, ctx);
       return;
     }
 
     if (res > messageLength) {
       LOG_GENERAL(WARNING,
                   "Error: Received msg len is greater than header msg len")
-      CloseAndFreeBevP2PSeedConn(bev);
+      CloseAndFreeBevP2PSeedConnClient(bev, ctx);
       return;
     } else if (res < messageLength) {
       return;
     }
   }
 
-  unique_ptr<struct bufferevent, decltype(&CloseAndFreeBevP2PSeedConn)>
-      socket_closer(bev, CloseAndFreeBevP2PSeedConn);
-
   if (evbuffer_drain(input, len) != 0) {
     LOG_GENERAL(WARNING, "Error: evbuffer_drain failure.");
+    CloseAndFreeBevP2PSeedConnClient(bev, ctx);
     return;
   }
 
@@ -1144,6 +1188,7 @@ void P2PComm ::ReadCbClientSeed(struct bufferevent* bev,
     // Unexpected start byte. Drop this message
     LOG_CHECK_FAIL("Start byte", startByte, START_BYTE_SEED_TO_SEED_RESPONSE);
   }
+  CloseAndFreeBevP2PSeedConnClient(bev, ctx);
 }
 
 // timeout event every 2 secs
@@ -1310,6 +1355,7 @@ void P2PComm::EnableConnect() {
 void P2PComm::WriteMsgOnBufferEvent(struct bufferevent* bev,
                                     const bytes& message,
                                     const unsigned char& startByte) {
+  LOG_MARKER();
   uint32_t length = message.size();
   unsigned char buf[HDR_LEN] = {(unsigned char)(MSG_VERSION & 0xFF),
                                 (unsigned char)((CHAIN_ID >> 8) & 0XFF),
@@ -1344,9 +1390,25 @@ void P2PComm::SendMsgToSeedNodeOnWire(const Peer& peer, const Peer& fromPeer,
         LOG_GENERAL(WARNING, "Error: Bufferevent_socket_new failure.");
         return;
       }
+      uint32_t length = message.size();
+      unsigned char buf[HDR_LEN] = {(unsigned char)(MSG_VERSION & 0xFF),
+                                    (unsigned char)((CHAIN_ID >> 8) & 0XFF),
+                                    (unsigned char)(CHAIN_ID & 0xFF),
+                                    START_BYTE_SEED_TO_SEED_REQUEST,
+                                    (unsigned char)((length >> 24) & 0xFF),
+                                    (unsigned char)((length >> 16) & 0xFF),
+                                    (unsigned char)((length >> 8) & 0xFF),
+                                    (unsigned char)(length & 0xFF)};
+      bytes destMsg(std::begin(buf), std::end(buf));
+      destMsg.insert(destMsg.end(), message.begin(), message.end());
+      LOG_GENERAL(DEBUG,
+                  "P2PSeed msg len=" << length + HDR_LEN << " bev=" << bev
+                                     << " destMsg size=" << destMsg.size());
+      bytes* destBytes = new bytes(std::move(destMsg));
       bufferevent_setwatermark(bev, EV_READ, MIN_READ_WATERMARK_IN_BYTES,
                                MAX_READ_WATERMARK_IN_BYTES);
-      bufferevent_setcb(bev, ReadCbClientSeed, NULL, EventCbClientSeed, NULL);
+      bufferevent_setcb(bev, ReadCbClientSeed, NULL, EventCbClientSeed,
+                        (void*)destBytes);
       bufferevent_enable(bev, EV_READ | EV_WRITE);
 
       struct timeval tv = {SEED_SYNC_LARGE_PULL_INTERVAL, 0};
@@ -1363,8 +1425,6 @@ void P2PComm::SendMsgToSeedNodeOnWire(const Peer& peer, const Peer& fromPeer,
         bufferevent_free(bev);
         return;
       }
-      WriteMsgOnBufferEvent(bev, message, START_BYTE_SEED_TO_SEED_REQUEST);
-
     } else {
       // seedpub response message
       LOG_GENERAL(INFO, "P2PSeed response msg peer=" << fromPeer);
```

### src/libNetwork/P2PComm.h
```diff
@@ -124,12 +124,11 @@ class P2PComm {
   static void EventCbServerSeed(struct bufferevent* bev, short events,
                                 [[gnu::unused]] void* ctx);
   static void EventCbClientSeed([[gnu::unused]] struct bufferevent* bev,
-                                short events, [[gnu::unused]] void* ctx);
+                                short events, void* ctx);
   static void ReadCallback(struct bufferevent* bev, void* ctx);
   static void ReadCbServerSeed(struct bufferevent* bev,
                                [[gnu::unused]] void* ctx);
-  static void ReadCbClientSeed(struct bufferevent* bev,
-                               [[gnu::unused]] void* ctx);
+  static void ReadCbClientSeed(struct bufferevent* bev, void* ctx);
 
   static void AcceptConnectionCallback(evconnlistener* listener,
                                        evutil_socket_t cli_sock,
@@ -140,7 +139,9 @@ class P2PComm {
                                  struct sockaddr* cli_addr, int socklen,
                                  void* arg);
   static void CloseAndFreeBufferEvent(struct bufferevent* bufev);
-  static void CloseAndFreeBevP2PSeedConn(struct bufferevent* bufev);
+  static void CloseAndFreeBevP2PSeedConnServer(struct bufferevent* bufev);
+  static void CloseAndFreeBevP2PSeedConnClient(struct bufferevent* bufev,
+                                               void* ctx);
 
  public:
   static std::mutex m_mutexBufferEvent;
```
