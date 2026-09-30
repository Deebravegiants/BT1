# [?] fix: prevent panic in VmStateIterator back() method when at clock 0 (#1825)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2025-05-21
Source: https://github.com/0xMiden/miden-vm/commit/d2e68e6c9f7049096b66daf490c22da0fd408f9d
Type: security-commit

## Details
fix: prevent panic in VmStateIterator back() method when at clock 0 (#1825)

* Update debug.rs

* changelog

---------

Co-authored-by: Philippe Laferriere <plafer@proton.me>

## Patch
### CHANGELOG.md
```diff
@@ -5,6 +5,9 @@
 #### Changes
 - Improve error messages for some assembler instruction (#1785)
 
+#### Fixes
+- `miden debug` rewind command no longer panics at clock 0 (#1751)
+
 
 ## 0.14.0 (2025-05-07)
 
```

### processor/src/debug.rs
```diff
@@ -169,7 +169,8 @@ impl VmStateIterator {
             memory: self.chiplets.memory.get_state_at(ctx, self.clk),
         });
 
-        self.clk -= 1;
+        // Use saturating_sub to prevent underflow when at clock 0
+        self.clk = self.clk.saturating_sub(1);
 
         result
     }
```
