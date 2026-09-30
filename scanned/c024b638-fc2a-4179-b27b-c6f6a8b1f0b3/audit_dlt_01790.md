# [?] Fix a race condition with TrustedPublisherServer:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2020-07-25
Source: https://github.com/XRPLF/rippled/commit/d317060ae455dd31251bfe5d7d391c9c72420cd3
Type: security-commit

## Details
Fix a race condition with TrustedPublisherServer:

There was a race condition in `on_accept` where the object's destructor
could run while `on_accept` was called.

This patch ensures that if `on_accept` is called then the object remains
valid for the duration of the call.

## Patch
### src/test/app/ValidatorSite_test.cpp
```diff
@@ -164,7 +164,7 @@ class ValidatorSite_test : public beast::unit_test::suite
             publisher(FetchListConfig const& c) : cfg{c}
             {
             }
-            std::unique_ptr<TrustedPublisherServer> server;
+            std::shared_ptr<TrustedPublisherServer> server;
             std::vector<Validator> list;
             std::string uri;
             FetchListConfig const& cfg;
@@ -184,7 +184,7 @@ class ValidatorSite_test : public beast::unit_test::suite
             while (item.list.size() < listSize)
                 item.list.push_back(TrustedPublisherServer::randomValidator());
 
-            item.server = std::make_unique<TrustedPublisherServer>(
+            item.server = make_TrustedPublisherServer(
                 env.app().getIOService(),
                 item.list,
                 env.timeKeeper().now() + cfg.expiresFromNow,
```

### src/test/jtx/TrustedPublisherServer.h
```diff
@@ -34,12 +34,15 @@
 #include <boost/beast/version.hpp>
 #include <boost/lexical_cast.hpp>
 #include <test/jtx/envconfig.h>
+
+#include <memory>
 #include <thread>
 
 namespace ripple {
 namespace test {
 
 class TrustedPublisherServer
+    : public std::enable_shared_from_this<TrustedPublisherServer>
 {
     using endpoint_type = boost::asio::ip::tcp::endpoint;
     using address_type = boost::asio::ip::address;
@@ -141,6 +144,10 @@ class TrustedPublisherServer
                 1)};
     }
 
+    // TrustedPublisherServer must be accessed through a shared_ptr
+    // This constructor is only public so std::make_shared has access.
+    // The function`make_TrustedPublisherServer` should be used to create
+    // instances.
     TrustedPublisherServer(
         boost::asio::io_context& ioc,
         std::vector<Validator> const& validators,
@@ -192,9 +199,6 @@ class TrustedPublisherServer
             // This holds the self-signed certificate used by the server
             load_server_certificate();
         }
-
-        if (immediateStart)
-            start();
     }
 
     void
@@ -208,10 +212,13 @@ class TrustedPublisherServer
         acceptor_.listen(boost::asio::socket_base::max_connections);
         acceptor_.async_accept(
             sock_,
-            std::bind(
-                &TrustedPublisherServer::on_accept,
-                this,
-                std::placeholders::_1));
+            [wp = std::weak_ptr<TrustedPublisherServer>{shared_from_this()}](
+                error_code ec) {
+                if (auto p = wp.lock())
+                {
+                    p->on_accept(ec);
+                }
+            });
     }
 
     void
@@ -442,19 +449,20 @@ gVyCOWoVCfgu37H5e7ERyoAxigiP8hMqoGpmJUYJghVKWoFgNUqXw+guVJ56eIuH
     void
     on_accept(error_code ec)
     {
-        // ec must be checked before `acceptor_` or the member variable may be
-        // accessed after the destructor has completed
         if (ec || !acceptor_.is_open())
             return;
 
         static int id_ = 0;
         std::thread{lambda{++id_, *this, std::move(sock_), useSSL_}}.detach();
         acceptor_.async_accept(
             sock_,
-            std::bind(
-                &TrustedPublisherServer::on_accept,
-                this,
-                std::placeholders::_1));
+            [wp = std::weak_ptr<TrustedPublisherServer>{shared_from_this()}](
+                error_code ec) {
+                if (auto p = wp.lock())
+                {
+                    p->on_accept(ec);
+                }
+            });
     }
 
     void
@@ -606,6 +614,23 @@ gVyCOWoVCfgu37H5e7ERyoAxigiP8hMqoGpmJUYJghVKWoFgNUqXw+guVJ56eIuH
     }
 };
 
+inline std::shared_ptr<TrustedPublisherServer>
+make_TrustedPublisherServer(
+    boost::asio::io_context& ioc,
+    std::vector<TrustedPublisherServer::Validator> const& validators,
+    NetClock::time_point expiration,
+    bool useSSL = false,
+    int version = 1,
+    bool immediateStart = true,
+    int sequence = 1)
+{
+    auto const r = std::make_shared<TrustedPublisherServer>(
+        ioc, validators, expiration, useSSL, version, sequence);
+    if (immediateStart)
+        r->start();
+    return r;
+}
+
 }  // namespace test
 }  // namespace ripple
 #endif
```

### src/test/net/DatabaseDownloader_test.cpp
```diff
@@ -31,16 +31,16 @@ namespace test {
 
 class DatabaseDownloader_test : public beast::unit_test::suite
 {
-    TrustedPublisherServer
+    std::shared_ptr<TrustedPublisherServer>
     createServer(jtx::Env& env, bool ssl = true)
     {
         std::vector<TrustedPublisherServer::Validator> list;
         list.push_back(TrustedPublisherServer::randomValidator());
-        return TrustedPublisherServer{
+        return make_TrustedPublisherServer(
             env.app().getIOService(),
             list,
             env.timeKeeper().now() + std::chrono::seconds{3600},
-            ssl};
+            ssl);
     }
 
     struct DownloadCompleter
@@ -129,8 +129,8 @@ class DatabaseDownloader_test : public beast::unit_test::suite
         // initiate the download and wait for the callback
         // to be invoked
         auto stat = downloader->download(
-            server.local_endpoint().address().to_string(),
-            std::to_string(server.local_endpoint().port()),
+            server->local_endpoint().address().to_string(),
+            std::to_string(server->local_endpoint().port()),
             "/textfile",
             11,
             data.file(),
@@ -196,9 +196,9 @@ class DatabaseDownloader_test : public beast::unit_test::suite
             ripple::test::detail::FileDirGuard const datafile{
                 *this, "downloads", "data", "", false, false};
             auto server = createServer(env);
-            auto host = server.local_endpoint().address().to_string();
-            auto port = std::to_string(server.local_endpoint().port());
-            server.stop();
+            auto host = server->local_endpoint().address().to_string();
+            auto port = std::to_string(server->local_endpoint().port());
+            server->stop();
             BEAST_EXPECT(dl->download(
                 host,
                 port,
@@ -220,8 +220,8 @@ class DatabaseDownloader_test : public beast::unit_test::suite
                 *this, "downloads", "data", "", false, false};
             auto server = createServer(env, false);
             BEAST_EXPECT(dl->download(
-                server.local_endpoint().address().to_string(),
-                std::to_string(server.local_endpoint().port()),
+                server->local_endpoint().address().to_string(),
+                std::to_string(server->local_endpoint().port()),
                 "",
                 11,
                 datafile.file(),
@@ -240,8 +240,8 @@ class DatabaseDownloader_test : public beast::unit_test::suite
                 *this, "downloads", "data", "", false, false};
             auto server = createServer(env);
             BEAST_EXPECT(dl->download(
-                server.local_endpoint().address().to_string(),
-                std::to_string(server.local_endpoint().port()),
+                server->local_endpoint().address().to_string(),
+                std::to_string(server->local_endpoint().port()),
                 "/textfile/huge",
                 11,
                 datafile.file(),
```

### src/test/rpc/ShardArchiveHandler_test.cpp
```diff
@@ -36,16 +36,16 @@ class ShardArchiveHandler_test : public beast::unit_test::suite
 {
     using Downloads = std::vector<std::pair<std::uint32_t, std::string>>;
 
-    TrustedPublisherServer
+    std::shared_ptr<TrustedPublisherServer>
     createServer(jtx::Env& env, bool ssl = true)
     {
         std::vector<TrustedPublisherServer::Validator> list;
         list.push_back(TrustedPublisherServer::randomValidator());
-        return TrustedPublisherServer{
+        return make_TrustedPublisherServer(
             env.app().getIOService(),
             list,
             env.timeKeeper().now() + std::chrono::seconds{3600},
-            ssl};
+            ssl);
     }
 
 public:
@@ -191,9 +191,9 @@ class ShardArchiveHandler_test : public beast::unit_test::suite
         BEAST_EXPECT(dynamic_cast<RPC::RecoveryHandler*>(handler) == nullptr);
 
         auto server = createServer(env);
-        auto host = server.local_endpoint().address().to_string();
-        auto port = std::to_string(server.local_endpoint().port());
-        server.stop();
+        auto host = server->local_endpoint().address().to_string();
+        auto port = std::to_string(server->local_endpoint().port());
+        server->stop();
 
         Downloads const dl = [count = numberOfDownloads, &host, &port] {
             Downloads ret;
@@ -290,9 +290,9 @@ class ShardArchiveHandler_test : public beast::unit_test::suite
                 dynamic_cast<RPC::RecoveryHandler*>(handler) == nullptr);
 
             auto server = createServer(env);
-            auto host = server.local_endpoint().address().to_string();
-            auto port = std::to_string(server.local_endpoint().port());
-            server.stop();
+            auto host = server->local_endpoint().address().to_string();
+            auto port = std::to_string(server->local_endpoint().port());
+            server->stop();
 
             Downloads const dl = [count = numberOfDownloads, &host, &port] {
                 Downloads ret;
```

### src/test/rpc/ValidatorRPC_test.cpp
```diff
@@ -190,8 +190,8 @@ class ValidatorRPC_test : public beast::unit_test::suite
         BasicApp worker{1};
         using namespace std::chrono_literals;
         NetClock::time_point const expiration{3600s};
-        TrustedPublisherServer server{
-            worker.get_io_service(), validators, expiration, false, 1, false};
+        auto server = make_TrustedPublisherServer(
+            worker.get_io_service(), validators, expiration, false, 1, false);
 
         //----------------------------------------------------------------------
         // Publisher list site unavailable
@@ -206,7 +206,7 @@ class ValidatorRPC_test : public beast::unit_test::suite
                 envconfig([&](std::unique_ptr<Config> cfg) {
                     cfg->section(SECTION_VALIDATOR_LIST_SITES).append(siteURI);
                     cfg->section(SECTION_VALIDATOR_LIST_KEYS)
-                        .append(strHex(server.publisherPublic()));
+                        .append(strHex(server->publisherPublic()));
                     return cfg;
                 }),
             };
@@ -245,7 +245,7 @@ class ValidatorRPC_test : public beast::unit_test::suite
                     BEAST_EXPECT(!jp.isMember(jss::version));
                     BEAST_EXPECT(
                         jp[jss::pubkey_publisher] ==
-                        strHex(server.publisherPublic()));
+                        strHex(server->publisherPublic()));
                 }
                 BEAST_EXPECT(jrr[jss::signing_keys].size() == 0);
             }
@@ -264,18 +264,18 @@ class ValidatorRPC_test : public beast::unit_test::suite
         //----------------------------------------------------------------------
         // Publisher list site available
         {
-            server.start();
+            server->start();
 
             std::stringstream uri;
-            uri << "http://" << server.local_endpoint() << "/validators";
+            uri << "http://" << server->local_endpoint() << "/validators";
             auto siteURI = uri.str();
 
             Env env{
                 *this,
                 envconfig([&](std::unique_ptr<Config> cfg) {
                     cfg->section(SECTION_VALIDATOR_LIST_SITES).append(siteURI);
                     cfg->section(SECTION_VALIDATOR_LIST_KEYS)
-                        .append(strHex(server.publisherPublic()));
+                        .append(strHex(server->publisherPublic()));
                     return cfg;
                 }),
             };
@@ -333,7 +333,7 @@ class ValidatorRPC_test : public beast::unit_test::suite
                     BEAST_EXPECT(jp[jss::seq].asUInt() == 1);
                     BEAST_EXPECT(
                         jp[jss::pubkey_publisher] ==
-                        strHex(server.publisherPublic()));
+                        strHex(server->publisherPublic()));
                     BEAST_EXPECT(jp[jss::expiration] == to_string(expiration));
                     BEAST_EXPECT(jp[jss::version] == 1);
                 }
```
