# [?] Merge pull request #3297 from pyth-network/cprussin/CVE-2025-55184

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2025-12-12
Source: https://github.com/pyth-network/pyth-crosschain/commit/3efdf8790d486da0ca1833ffe2bcc115eb0232af
Type: security-commit

## Details
Merge pull request #3297 from pyth-network/cprussin/CVE-2025-55184

chore: upgrade next & react

## Patch
### pnpm-workspace.yaml
```diff
@@ -98,8 +98,8 @@ catalog:
   "@types/mdx": ^2.0.13
   "@types/node": ^22.14.0
   "@types/prompts": 2.4.9
-  "@types/react": ^19.1.0
-  "@types/react-dom": ^19.1.1
+  "@types/react": ^19.1.4
+  "@types/react-dom": ^19.1.4
   "@types/yargs": "^17.0.33"
   "@vercel/functions": ^2.0.0
   "ag-grid-community": ^34.2.0
@@ -140,7 +140,7 @@ catalog:
   micromustache: ^8.0.3
   modern-normalize: ^3.0.1
   motion: ^12.9.2
-  next: ^15.5.7
+  next: ^15.5.9
   next-themes: ^0.4.6
   nuqs: ^2.4.1
   pino: ^9.6.0
@@ -150,10 +150,10 @@ catalog:
   prettier-plugin-solidity: ^1.4.2
   prompts: 2.4.2
   proxycheck-ts: ^0.0.11
-  react: ^19.1.2
+  react: ^19.1.4
   react-aria: ^3.42.0
   react-aria-components: ^1.11.0
-  react-dom: ^19.1.2
+  react-dom: ^19.1.4
   react-markdown: ^10.1.0
   react-timeago: ^8.2.0
   recharts: ^2.15.1
```
