# [?] fix(PocketIC): panic in SystemTime::elapsed (#5255)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-05-22
Source: https://github.com/dfinity/ic/commit/e767ee3ddf3ea3d3a0a453c24a172cc970ee0669
Type: security-commit

## Details
fix(PocketIC): panic in SystemTime::elapsed (#5255)

This PR fixes test failures such as
[this](https://github.com/dfinity/ic/actions/runs/15183560437/job/42703402902?pr=5234#step:5:13075)
due to `SystemTime` not being monotone.

## Patch
### packages/pocket-ic/src/nonblocking.rs
```diff
@@ -1567,7 +1567,8 @@ impl PocketIc {
                             }
                         }
                         if let Some(max_request_time_ms) = self.max_request_time_ms {
-                            if start.elapsed().unwrap() > Duration::from_millis(max_request_time_ms)
+                            if start.elapsed().unwrap_or_default()
+                                > Duration::from_millis(max_request_time_ms)
                             {
                                 panic!("request to PocketIC server timed out.");
                             }
@@ -1576,7 +1577,8 @@ impl PocketIc {
                 }
             }
             if let Some(max_request_time_ms) = self.max_request_time_ms {
-                if start.elapsed().unwrap() > Duration::from_millis(max_request_time_ms) {
+                if start.elapsed().unwrap_or_default() > Duration::from_millis(max_request_time_ms)
+                {
                     panic!("request to PocketIC server timed out.");
                 }
             }
```
