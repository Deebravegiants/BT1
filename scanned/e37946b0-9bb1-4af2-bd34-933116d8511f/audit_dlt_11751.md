# [?] Merge pull request #4527 from natsee/fix-faq-nav-bar-overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-01-03
Source: https://github.com/mempool/mempool/commit/56dce6b28c2ae2551d7e89caac24d8214a2fb077
Type: security-commit

## Details
Merge pull request #4527 from natsee/fix-faq-nav-bar-overflow

Fix faq nav bar overflow

## Patch
### frontend/src/app/docs/api-docs/api-docs.component.scss
```diff
@@ -157,7 +157,7 @@ ul.no-bull.block-audit code{
   position: fixed;
   top: 80px;
   overflow-y: auto;
-  height: calc(100vh - 50px);
+  height: calc(100vh - 75px);
   scrollbar-color: #2d3348 #11131f;
   scrollbar-width: thin;
 }
```
