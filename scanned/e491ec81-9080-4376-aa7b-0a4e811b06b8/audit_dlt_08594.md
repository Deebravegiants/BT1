# [?] Fix use after free error in test code

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2017-07-18
Source: https://github.com/XRPLF/rippled/commit/a79cb95c85237adb5ab210e6949776ac00cabdfb
Type: security-commit

## Details
Fix use after free error in test code

## Patch
### src/test/app/ValidatorSite_test.cpp
```diff
@@ -125,10 +125,11 @@ class http_sync_server
     void
     on_accept(error_code ec)
     {
-        if(! acceptor_.is_open())
-            return;
-        if(ec)
+        // ec must be checked before `acceptor_` or the member variable may be
+        // accessed after the destructor has completed
+        if(ec || !acceptor_.is_open())
             return;
+
         static int id_ = 0;
         std::thread{lambda{++id_, *this, std::move(sock_)}}.detach();
         acceptor_.async_accept(sock_,
```
