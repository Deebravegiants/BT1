# [?] fix(developer-hub): fix PageActions mobile layout overflow

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2025-11-26
Source: https://github.com/pyth-network/pyth-crosschain/commit/41d78bfe7b61c8cffa6b60c1f5d3b2179408b5d2
Type: security-commit

## Details
fix(developer-hub): fix PageActions mobile layout overflow

Make the PageActions container responsive on mobile by allowing
buttons to wrap and enabling horizontal scrolling. On screens
smaller than 640px (sm breakpoint), the buttons will wrap to
multiple lines or scroll horizontally instead of overflowing
and blocking the page content.

Co-Authored-By: aditya@dourolabs.xyz <aditya@dourolabs.xyz>

## Patch
### apps/developer-hub/src/components/PageActions/index.module.scss
```diff
@@ -11,6 +11,14 @@
   display: flex;
   align-items: center;
   gap: 0;
+  flex-wrap: wrap;
+  overflow-x: auto;
+  -webkit-overflow-scrolling: touch;
+
+  @include theme.breakpoint("sm") {
+    flex-wrap: nowrap;
+    overflow-x: visible;
+  }
 }
 
 .buttonWrapper {
```
