# [?] fix(pnpm): Fix CVE-2025-58754, update axios to 1.12.0 (#8542)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-09-12
Source: https://github.com/iotaledger/iota/commit/d0aa22014de16c0257ceed6d90cc1f39c6c7281b
Type: security-commit

## Details
fix(pnpm): Fix CVE-2025-58754, update axios to 1.12.0 (#8542)

Fixes https://github.com/advisories/GHSA-4hjh-wcwx-xvwj


https://github.com/iotaledger/iota/actions/runs/17668092142/job/50213546292?pr=8492

The actual issue does not affect us as we dont use axios in nodejs.

## Patch
### .changeset/weak-laws-promise.md
```diff
@@ -0,0 +1,5 @@
+---
+'@iota/ledgerjs-hw-app-iota': minor
+---
+
+Updates Axios to 1.12.0
```

### apps/wallet/package.json
```diff
@@ -115,7 +115,7 @@
         "@sentry/browser": "^7.120.3",
         "@tanstack/react-query": "^5.50.1",
         "@tanstack/react-query-persist-client": "^5.40.1",
-        "axios": "^1.8.2",
+        "axios": "^1.12.0",
         "bignumber.js": "^9.1.1",
         "buffer": "^6.0.3",
         "class-variance-authority": "^0.7.0",
```

### docs/site/package.json
```diff
@@ -43,7 +43,7 @@
     "@saucelabs/theme-github-codeblock": "^0.3.0",
     "@tanstack/react-query": "^5.50.1",
     "autoprefixer": "^10.4.19",
-    "axios": "^1.8.2",
+    "axios": "^1.12.0",
     "clsx": "^2.1.1",
     "docusaurus-plugin-openapi-docs": "^4.3.7",
     "docusaurus-theme-openapi-docs": "^4.3.7",
```

### sdk/ledgerjs-hw-app-iota/package.json
```diff
@@ -69,7 +69,7 @@
         "@ledgerhq/hw-transport-node-speculos-http": "^6.29.2",
         "@size-limit/preset-small-lib": "^11.1.4",
         "@types/node": "^20.14.10",
-        "axios": "^1.8.2",
+        "axios": "^1.12.0",
         "size-limit": "^11.1.4",
         "typescript": "^5.5.3",
         "vitest": "^2.1.9"
```
