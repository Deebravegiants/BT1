# [?] dex: 🌸 apply "fix chain halt in testnet 68" to main (#3950)

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2024-03-05
Source: https://github.com/penumbra-zone/penumbra/commit/98c42d8f09200ed41771c4dad91e5997bb4a0cab
Type: security-commit

## Details
dex: 🌸 apply "fix chain halt in testnet 68" to main (#3950)

Testnet 68 halted at height 100736, with an `.expect` here:


https://github.com/penumbra-zone/penumbra/blob/1c99e24ad5cf1ecc2855849d66221ecec25f9235/crates/core/component/dex/src/component/dex.rs#L66

This hit an error bubbled up from here:


https://github.com/penumbra-zone/penumbra/blob/1c99e24ad5cf1ecc2855849d66221ecec25f9235/crates/core/component/dex/src/component/router/route_and_fill.rs#L277

The error occurs in this method, which is only ever used at that
callsite:


https://github.com/penumbra-zone/penumbra/blob/1c99e24ad5cf1ecc2855849d66221ecec25f9235/crates/core/component/dex/src/swap_execution.rs#L18

It's a little unclear why that method has double fallibility.
Unfortunately, the answer may not be easily determined. It was added
here


https://github.com/penumbra-zone/penumbra/commit/9cd566daf098a52eac3283ea20fe4949181fe67f

which indicates that there was previously an infallible `max_price`, but
that code isn't included in the commit; the previous reference to an
infallible `max_price` was added in this commit


https://github.com/penumbra-zone/penumbra/commit/b4b26351db0d042bd661c6733f7182f22b323e0d

which doesn't have the impl either, so presumably it got mangled during
rebasing.

In any case, removing the double fallibility, as in this commit, allows
committing block 100736 on testnet 68, which I verified by running this
code against a local copy of a state snapshot.

Co-authored-by: Henry de Valence <hdevalence@penumbralabs.xyz>

### crates/core/component/dex/src/component/router/route_and_fill.rs
```diff
@@ -274,7 +274,7 @@ pub trait RouteAndFill: StateWrite + Sized {
             }
 
             // Ensure that we've actually executed, or else bail out.
-            let Some(accurate_max_price) = execution.max_price()? else {
+            let Some(accurate_max_price) = execution.max_price() else {
                 tracing::debug!("no traces in execution, exiting route_and_fill");
                 break;
             };
```

### crates/core/component/dex/src/swap_execution.rs
```diff
@@ -15,17 +15,17 @@ pub struct SwapExecution {
 
 impl SwapExecution {
     /// Returns the price of the latest execution trace.
-    pub fn max_price(&self) -> Result<Option<U128x128>> {
+    pub fn max_price(&self) -> Option<U128x128> {
         let Some((input, output)) = self.traces.last().and_then(|trace| {
             let input = trace.first()?;
             let output = trace.last()?;
             Some((input, output))
         }) else {
-            return Ok(None);
+            return None;
         };
 
-        let price = U128x128::ratio(input.amount, output.amount)?;
-        Ok(Some(price))
+        let price = U128x128::ratio(input.amount, output.amount).ok()?;
+        Some(price)
     }
 }
 
```
