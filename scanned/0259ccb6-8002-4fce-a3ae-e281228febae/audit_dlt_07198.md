# [?] fix(ux): Disable issue URLs for a known shutdown panic in abscissa (#6486)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-04-14
Source: https://github.com/ZcashFoundation/zebra/commit/cf6d0cc2d596b11cfdea868f8a4ab6a35da24765
Type: security-commit

## Details
fix(ux): Disable issue URLs for a known shutdown panic in abscissa (#6486)

* Disable bug report URLs for a known abscissa panic

* Remove trailing whitespace in deny.toml

* upddate doc

Co-authored-by: Deirdre Connolly <durumcrustulum@gmail.com>

---------

Co-authored-by: Alfredo Garcia <oxarbitrage@gmail.com>
Co-authored-by: Deirdre Connolly <durumcrustulum@gmail.com>

## Patch
### deny.toml
```diff
@@ -90,7 +90,7 @@ skip-tree = [
     # wait for console-subscriber and tower to update hdrhistogram.
     # also wait for ron to update insta, and wait for tonic update.
     { name = "base64", version = "=0.13.1" },
-    
+
     # wait for proptest's rusty-fork dependency to upgrade quick-error
     { name = "quick-error", version = "=1.2.3" },
 
```

### zebrad/src/application.rs
```diff
@@ -1,8 +1,5 @@
 //! Zebrad Abscissa Application
 
-mod entry_point;
-use self::entry_point::EntryPoint;
-
 use std::{fmt::Write as _, io::Write as _, process};
 
 use abscissa_core::{
@@ -18,6 +15,9 @@ use zebra_state::constants::{DATABASE_FORMAT_VERSION, LOCK_FILE_ERROR};
 
 use crate::{commands::ZebradCmd, components::tracing::Tracing, config::ZebradConfig};
 
+mod entry_point;
+use entry_point::EntryPoint;
+
 /// See <https://docs.rs/abscissa_core/latest/src/abscissa_core/application/exit.rs.html#7-10>
 /// Print a fatal error message and exit
 fn fatal_error(app_name: String, err: &dyn std::error::Error) -> ! {
@@ -309,10 +309,14 @@ impl Application for ZebradApp {
                         return false;
                     }
 
+                    // Don't ask users to create bug reports for known timeouts, duplicate blocks,
+                    // full disks, or updated binaries.
                     let error_str = error.to_string();
                     !error_str.contains("timed out")
                         && !error_str.contains("duplicate hash")
                         && !error_str.contains("No space left on device")
+                        // abscissa panics like this when the running zebrad binary has been updated
+                        && !error_str.contains("error canonicalizing application path")
                 }
             });
 
```
