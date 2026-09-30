# [?] fix: remove short name for --host to resolve pviewd runtime panic

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-06-15
Source: https://github.com/penumbra-zone/penumbra/commit/cdbeb0f8130cf3e3895fdc3ab2fc9c8eb8dc5474
Type: security-commit

## Details
fix: remove short name for --host to resolve pviewd runtime panic

This was happening due to a conflict with --help/-h short name.
Same issue as #995 which was happening in pd and caught by the smoke
test. This issue was discovered by testers in #validator-discussion.

## Patch
### view/src/bin/pviewd.rs
```diff
@@ -46,7 +46,7 @@ enum Command {
     /// Start the view service.
     Start {
         /// Bind the view service to this host.
-        #[clap(short, long, default_value = "127.0.0.1")]
+        #[clap(long, default_value = "127.0.0.1")]
         host: String,
         /// Bind the view gRPC server to this port.
         #[clap(long, default_value = "8081")]
```
