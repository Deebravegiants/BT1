# [?] release: ignore postcss vulnerabilities temporarily for release 13.41.0

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-07-24
Source: https://github.com/MetaMask/metamask-extension/commit/59a4a4a89fff59654a5e9248200d75a0a718a8fa
Type: security-commit

## Details
release: ignore postcss vulnerabilities temporarily for release 13.41.0

## Patch
### .yarnrc.yml
```diff
@@ -39,6 +39,13 @@ npmAuditIgnoreAdvisories:
   # There is no fix for this low-severity advisory
   - 1112030
 
+  # Issue: postcss vulnerability
+  # URL: https://github.com/advisories/GHSA-6g55-p6wh-862q
+  # URL: https://github.com/advisories/GHSA-r28c-9q8g-f849
+  # Ignoring these temporarily for release 13.41.0
+  - 1124288
+  - 1124252
+
   ### Package Deprecations:
 
   # React-tippy brings in popper.js and react-tippy has not been updated in
```
