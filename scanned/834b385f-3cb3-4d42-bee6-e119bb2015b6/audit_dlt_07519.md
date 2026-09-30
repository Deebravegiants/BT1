# [?] rpc: fix crash in deriveaddresses when derivation index is 2147483647

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2022-10-06
Source: https://github.com/ElementsProject/elements/commit/5a43eac4d3558432b8aa3292bcbbcaf4e1cc66f1
Type: security-commit

## Details
rpc: fix crash in deriveaddresses when derivation index is 2147483647

2147483647 is the maximum positive value of a signed int32, and - currently -
the maximum value that the deriveaddresses bitcoin RPC call accepts as
derivation index due to its input validation routines.

Before this change, when the derivation index (and thus range_end) reached
std::numeric_limits<int_32_t>::max(), the "i" variable in the for cycle (which
is declared as int, and as such 32 bits in size on most platforms) would be
incremented at the end of the first iteration and then warp back to
-2147483648. This caused SIGABRT in bitcoind and a core dump.

This change assigns "i" an explicit size of 64 bits on every platform,
sidestepping the problem.

Fixes #26274.

Github-Pull: #26275
Rebased-From: addf9d6502db12cebcc5976df3111cac1a369b82

## Patch
### src/rpc/misc.cpp
```diff
@@ -320,7 +320,7 @@ static RPCHelpMan deriveaddresses()
 
     UniValue addresses(UniValue::VARR);
 
-    for (int i = range_begin; i <= range_end; ++i) {
+    for (int64_t i = range_begin; i <= range_end; ++i) {
         FlatSigningProvider provider;
         std::vector<CScript> scripts;
         if (!desc->Expand(i, key_provider, scripts, provider)) {
```
