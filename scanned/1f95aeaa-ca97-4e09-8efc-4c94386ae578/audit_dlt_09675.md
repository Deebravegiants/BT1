# [?] fix crash/UB when exceeding max-requests-in-flight

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2024-02-05
Source: https://github.com/AntelopeIO/leap/commit/874b80ea2d19a09d8017a51232e057d1bc4ec3fe
Type: security-commit

## Details
fix crash/UB when exceeding max-requests-in-flight

## Patch
### plugins/http_plugin/include/eosio/http_plugin/beast_http_session.hpp
```diff
@@ -492,8 +492,9 @@ class beast_http_session : public detail::abstract_conn,
 
    void run_session() {
       if(auto error_str = verify_max_requests_in_flight(); !error_str.empty()) {
+         res_->keep_alive(false);
          send_busy_response(std::move(error_str));
-         return do_eof();
+         return;
       }
 
       do_read_header();
```
