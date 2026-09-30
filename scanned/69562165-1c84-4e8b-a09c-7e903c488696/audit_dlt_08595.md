# [?] Server deadlock fixes

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2016-02-09
Source: https://github.com/XRPLF/rippled/commit/ba38bfad9deab876d89600bb080a6fb49d84f5be
Type: security-commit

## Details
Server deadlock fixes

## Patch
### src/ripple/server/impl/Door.cpp
```diff
@@ -170,8 +170,6 @@ Door::Door (boost::asio::io_service& io_service,
         //port_->protocol.count("ws") > 0 ||
         port_->protocol.count("http") > 0)
 {
-    server_.add (*this);
-
     error_code ec;
     endpoint_type const local_address =
         endpoint_type(port.ip, port.port);
@@ -221,7 +219,6 @@ Door::~Door()
         while (! list_.empty())
             cond_.wait(lock);
     }
-    server_.remove (*this);
 }
 
 void
@@ -240,12 +237,21 @@ Door::close()
     error_code ec;
     acceptor_.close(ec);
     // Close all detector, Peer objects
-    std::lock_guard<std::mutex> lock(mutex_);
-    for(auto& _ : list_)
+    std::vector<std::shared_ptr<Child>> v;
     {
-        auto const peer = _.second.lock();
-        if (peer != nullptr)
-            peer->close();
+        std::lock_guard<std::mutex> lock(mutex_);
+        for(auto& p : list_)
+        {
+            auto const peer = p.second.lock();
+            if (peer != nullptr)
+            {
+                peer->close();
+                // Must destroy shared_ptr outside the
+                // lock otherwise deadlock from the
+                // managed object's destructor.
+                v.emplace_back(std::move(peer));
+            }
+        }
     }
 }
 
@@ -321,7 +327,9 @@ Door::do_accept (boost::asio::yield_context yield)
                 std::move(socket), remote_address);
         }
     }
+    server_.remove();
 }
 
 }
-}
+} // ripple
+
```

### src/ripple/server/impl/ServerImpl.cpp
```diff
@@ -37,7 +37,7 @@ namespace HTTP {
 
 ServerImpl::ServerImpl (Handler& handler,
         boost::asio::io_service& io_service, beast::Journal journal)
-    : handler_ (handler)
+    : handler_ (&handler)
     , journal_ (journal)
     , io_service_ (io_service)
     , strand_ (io_service_)
@@ -48,11 +48,13 @@ ServerImpl::ServerImpl (Handler& handler,
 
 ServerImpl::~ServerImpl()
 {
+    // Prevent call to handler
+    handler_ = nullptr;
     close();
     {
-        // Block until all Door objects destroyed
+        // Block until all Doors are done accepting
         std::unique_lock<std::mutex> lock(mutex_);
-        while (! list_.empty())
+        while (accepting_ > 0)
             cond_.wait(lock);
     }
 }
@@ -62,10 +64,17 @@ ServerImpl::ports (std::vector<Port> const& ports)
 {
     if (closed())
         Throw<std::logic_error> ("ports() on closed HTTP::Server");
-    for(auto const& _ : ports)
-        if (! _.websockets())
-            std::make_shared<Door>(
-                io_service_, *this, _)->run();
+    for(auto const& port : ports)
+    {
+        if (! port.websockets())
+        {
+            ++accepting_;
+            list_.emplace_back(std::make_shared<Door>(
+                io_service_, *this, port));
+        }
+    }
+    for(auto const& door : list_)
+        door->run();
 }
 
 void
@@ -109,48 +118,44 @@ ServerImpl::onWrite (beast::PropertyStream::Map& map)
 void
 ServerImpl::close()
 {
-    bool stopped = false;
+    Handler* h = nullptr;
     {
         std::lock_guard<std::mutex> lock(mutex_);
         if (work_)
         {
             work_ = boost::none;
             // Close all Door objects
-            if (list_.empty())
-                stopped = true;
+            if (accepting_ == 0)
+            {
+                std::swap (h, handler_);
+            }
             else
-                for(auto& _ :list_)
-                    _.close();
+            {
+                for(auto& door : list_)
+                    door->close();
+            }
         }
     }
-    if (stopped)
-        handler_.onStopped(*this);
+    if (h)
+        h->onStopped(*this);
 }
 
 //--------------------------------------------------------------------------
 
 void
-ServerImpl::add (Child& child)
-{
-    std::lock_guard<std::mutex> lock(mutex_);
-    list_.push_back(child);
-}
-
-void
-ServerImpl::remove (Child& child)
+ServerImpl::remove()
 {
-    bool stopped = false;
+    Handler* h = nullptr;
     {
         std::lock_guard<std::mutex> lock(mutex_);
-        list_.erase(list_.iterator_to(child));
-        if (list_.empty())
+        if(--accepting_ == 0)
         {
             cond_.notify_all();
-            stopped = true;
+            std::swap (h, handler_);
         }
     }
-    if (stopped)
-        handler_.onStopped(*this);
+    if (h)
+        h->onStopped(*this);
 }
 
 bool
```

### src/ripple/server/impl/ServerImpl.h
```diff
@@ -26,7 +26,6 @@
 #include <beast/intrusive/List.h>
 #include <beast/threads/Thread.h>
 #include <boost/asio.hpp>
-#include <boost/intrusive/list.hpp>
 #include <boost/optional.hpp>
 #include <array>
 #include <chrono>
@@ -55,17 +54,13 @@ struct Stat
 class ServerImpl : public Server
 {
 public:
-    class Child : public boost::intrusive::list_base_hook <
-        boost::intrusive::link_mode <boost::intrusive::normal_link>>
+    struct Child
     {
-    public:
+        virtual ~Child() = default;
         virtual void close() = 0;
     };
 
 private:
-    using list_type = boost::intrusive::make_list <Child,
-        boost::intrusive::constant_time_size <false>>::type;
-
     using clock_type = std::chrono::system_clock;
 
     enum
@@ -75,15 +70,16 @@ class ServerImpl : public Server
 
     using Doors = std::vector <std::shared_ptr<Door>>;
 
-    Handler& handler_;
+    Handler* handler_;
     beast::Journal journal_;
     boost::asio::io_service& io_service_;
     boost::asio::io_service::strand strand_;
     boost::optional <boost::asio::io_service::work> work_;
 
     std::mutex mutable mutex_;
     std::condition_variable cond_;
-    list_type list_;
+    std::vector<std::shared_ptr<Door>> list_;
+    std::size_t accepting_ = 0;
     std::deque <Stat> stats_;
     int high_ = 0;
 
@@ -114,7 +110,7 @@ class ServerImpl : public Server
     Handler&
     handler()
     {
-        return handler_;
+        return *handler_;
     }
 
     boost::asio::io_service&
@@ -124,10 +120,7 @@ class ServerImpl : public Server
     }
 
     void
-    add (Child& child);
-
-    void
-    remove (Child& child);
+    remove();
 
     bool
     closed();
```
