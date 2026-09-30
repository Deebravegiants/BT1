# [?] fix(compiler): sierra compiler crashes on macos

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-05-21
Source: https://github.com/software-mansion/pathfinder/commit/b97103fa1e18ae316e11330eca247761d84b5c48
Type: security-commit

## Details
fix(compiler): sierra compiler crashes on macos

## Patch
### crates/compiler/src/lib.rs
```diff
@@ -244,12 +244,15 @@ fn set_resource_limits(
     // variables etc. inside the closure.
     unsafe {
         cmd.pre_exec(move || {
-            let mem_limit = libc::rlimit {
-                rlim_cur: resource_limits.memory_usage,
-                rlim_max: resource_limits.memory_usage,
-            };
-            if libc::setrlimit(libc::RLIMIT_AS, &mem_limit) != 0 {
-                return Err(std::io::Error::last_os_error());
+            #[cfg(target_os = "linux")]
+            {
+                let mem_limit = libc::rlimit {
+                    rlim_cur: resource_limits.memory_usage,
+                    rlim_max: resource_limits.memory_usage,
+                };
+                if libc::setrlimit(libc::RLIMIT_AS, &mem_limit) != 0 {
+                    return Err(std::io::Error::last_os_error());
+                }
             }
 
             let cpu_limit = libc::rlimit {
```
