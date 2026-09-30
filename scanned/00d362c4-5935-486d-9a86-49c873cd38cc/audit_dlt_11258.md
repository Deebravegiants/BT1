# [?] fix(doc): code block overflow (#11308)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-23
Source: https://github.com/noir-lang/noir/commit/0d03696224885280fe55bed7309f09c8f631ef0b
Type: security-commit

## Details
fix(doc): code block overflow (#11308)

## Patch
### noir_stdlib/docs/styles.css
```diff
@@ -139,6 +139,10 @@ ul.item-list, ul.sidebar-list {
     font-family: "Source Serif 4", NanumBarunGothic, serif;
 }
 
+.comments pre {
+    overflow: auto;
+}
+
 .comments code, .item-description code {
     background-color: var(--code-color);
     border-radius: 6px;
```

### tooling/nargo_doc/src/styles.css
```diff
@@ -139,6 +139,10 @@ ul.item-list, ul.sidebar-list {
     font-family: "Source Serif 4", NanumBarunGothic, serif;
 }
 
+.comments pre {
+    overflow: auto;
+}
+
 .comments code, .item-description code {
     background-color: var(--code-color);
     border-radius: 6px;
```
