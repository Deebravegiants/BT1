# [?] Fix a rare race condition on shutdown:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2018-10-11
Source: https://github.com/XRPLF/rippled/commit/9ad2b9be45e768dc2bb088cf9fae71eaf11a7349
Type: security-commit

## Details
Fix a rare race condition on shutdown:

If we happen to get very unlucky and close the door when no
accept operation is pending, the do_accept loop would never
terminate.

## Patch
### src/ripple/server/impl/Door.h
```diff
@@ -369,7 +369,7 @@ void
 Door<Handler>::
 do_accept(boost::asio::yield_context do_yield)
 {
-    for(;;)
+    while (acceptor_.is_open())
     {
         error_code ec;
         endpoint_type remote_address;
```
