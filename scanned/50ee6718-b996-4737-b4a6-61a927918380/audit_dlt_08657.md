# [?] fix: Avoid jitter underflow and nearly infinite sleep (#10627)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-07-02
Source: https://github.com/dfinity/ic/commit/280f3b66c2585136453f10837d9eb7d8dacfe29a
Type: security-commit

## Details
fix: Avoid jitter underflow and nearly infinite sleep (#10627)

When investigating an issue with one of the type4 VMs, I found a sleep
that is scheduled for more than 200 years 😅.

## Patch
### rs/ic_os/device/src/io.rs
```diff
@@ -3,7 +3,7 @@ use std::io;
 use std::time::Duration;
 
 // TODO: Make this configurable
-const RETRY_MAX_ATTEMPTS: i32 = 10;
+const RETRY_MAX_ATTEMPTS: u32 = 10;
 
 /// Retries a function, returning its result if it succeeds, or retrying if it fails with
 /// the specified error.
@@ -23,7 +23,7 @@ pub fn retry_if_io_error<T>(
                     }
                     #[cfg(not(test))]
                     {
-                        let jitter = rand::random::<i32>() % 200;
+                        let jitter = rand::random::<u32>() % 200;
                         std::thread::sleep(Duration::from_millis((100 * attempts + jitter) as u64));
                     }
                 } else {
```
