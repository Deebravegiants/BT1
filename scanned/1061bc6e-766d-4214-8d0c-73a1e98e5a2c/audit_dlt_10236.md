# [?] prb: fix panic on retry

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2023-04-19
Source: https://github.com/Phala-Network/phala-blockchain/commit/06eec3321037322dda4db23a460b569d0d2debe2
Type: security-commit

## Details
prb: fix panic on retry

## Patch
### standalone/prb/src/api.rs
```diff
@@ -53,7 +53,6 @@ pub struct TxStatusResponse {
 
 impl IntoResponse for ApiError {
     fn into_response(self) -> Response {
-        warn!("{}", &self);
         match self {
             ApiError::ServerError(e) => {
                 let backtrace = e.backtrace().to_string();
```

### standalone/prb/src/utils.rs
```diff
@@ -27,7 +27,7 @@ macro_rules! with_retry {
                 Err(e) => {
                     warn!("Attempt #{retry_count}({}): {}", stringify!($f), &e);
                     retry_count += 1;
-                    if retry_count == ($c + 1) {
+                    if (retry_count - 1) == $c {
                         break Err(e);
                     }
                     tokio::time::sleep(std::time::Duration::from_millis($s)).await;
```
