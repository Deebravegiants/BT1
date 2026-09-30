# [?] patch other-version menu overflow [Fixes #14429] (#14431)

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2023-07-24
Source: https://github.com/argotorg/solidity/commit/4fa48a6eb1a1c33f60fc92e5895486dbdea294be
Type: security-commit

## Details
patch other-version menu overflow [Fixes #14429] (#14431)

## Patch
### docs/_static/css/custom.css
```diff
@@ -16,6 +16,7 @@
 
     --navHeight: 4.5rem;
     --sideWidth: 300px;
+    --currentVersionHeight: 45px;
 
     text-rendering: geometricPrecision;
     -webkit-font-smoothing: antialiased;
@@ -658,6 +659,8 @@ ul.search .context {
 .rst-other-versions {
     background: var(--white) !important;
     color: var(--color-a) !important;
+    max-height: calc(100vh - var(--navHeight) - var(--currentVersionHeight));
+    overflow-y: scroll;
 }
 
 .rst-other-versions a {
```
