# [?] avoid panicing when passed a non-utf8 log message

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/ref-fvm
Published: 2022-01-25
Source: https://github.com/filecoin-project/ref-fvm/commit/49f926e5d18edfb63c28eba5abcec356b0d1e3c0
Type: security-commit

## Details
avoid panicing when passed a non-utf8 log message

## Patch
### fvm/src/syscalls/debug.rs
```diff
@@ -1,10 +1,10 @@
-use crate::kernel::Result;
+use crate::kernel::{ClassifyResult, Result};
 use crate::syscalls::context::Context;
 use crate::Kernel;
 
 pub fn log(context: Context<'_, impl Kernel>, msg_off: u32, msg_len: u32) -> Result<()> {
     let msg = context.memory.try_slice(msg_off, msg_len)?;
-    let msg = String::from_utf8(msg.to_owned()).unwrap();
+    let msg = String::from_utf8(msg.to_owned()).or_illegal_argument()?;
     context.kernel.log(msg);
     Ok(())
 }
```
