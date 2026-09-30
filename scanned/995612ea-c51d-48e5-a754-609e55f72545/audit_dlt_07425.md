# [?] Fix for esoteric clang-7.0.1 crash

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-01-28
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/7e130484a9b911b3a0eea24a3897605da732d29f
Type: security-commit

## Details
Fix for esoteric clang-7.0.1 crash

Summary
---

Apparently, on some systems, clang-7.0.1 has bugs.  It dies on line 163
in `src/qt/guiutil.cpp` with a hard segfault.  See issue #242.

After conversations in slack and in issue #242, this 1-line patch fixes
the segfault.

Closes issue #242

Test Plan
---

- Use clang-7.0.1, see if you can reproduce the crash described in #242
  off master.
- If you can, use this branch and see that it fixes the crash when
  building using the same command-line as described in #242:
  - `cmake -GNinja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ ..`
  - `ninja all check-all`

## Patch
### src/qt/guiutil.cpp
```diff
@@ -160,7 +160,7 @@ bool parseBitcoinURI(const QString &scheme, const QUrl &uri,
     rv.amount = Amount::zero();
 
     const QUrlQuery uriQuery(uri);
-    for (auto & [key, value] : uriQuery.queryItems()) {
+    for (auto [key, value] : uriQuery.queryItems()) {
         bool required = false;
         if (key.startsWith("req-")) {
             key.remove(0, 4);
```
