# [?] chore: fix vulnerabilities, remove unused deps, update packages

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-03-30
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/4aed1dbe9494750553c697c7ccc2263869c6ef11
Type: security-commit

## Details
chore: fix vulnerabilities, remove unused deps, update packages

- Fix all 15 npm audit vulnerabilities (0 remaining)
- Update lerna 9.0.5 -> 9.0.7
- Remove deprecated eslint-plugin-node and eslint-plugin-standard
- Remove unused deps from sign-client (@walletconnect/events, heartbeat)
- Remove unused deps from ethereum-provider (jsonrpc-http-connection, logger)
- Update @reown/appkit from pre-release to stable 1.8.19
- Apply minor/patch updates: @rollup/plugin-commonjs, @typescript-eslint/*,
  prettier, rollup, sinon, es-toolkit, wait-on
- Add @react-native-async-storage override to resolve peer dep conflict
- Regenerate clean lockfile without --legacy-peer-deps

Made-with: Cursor

## Patch
### package.json
```diff
@@ -60,36 +60,35 @@
     "lodash": "^4.17.23",
     "vite": "^7.3.1",
     "axios": "^1.13.5",
-    "@isaacs/brace-expansion": "^5.0.1"
+    "@isaacs/brace-expansion": "^5.0.1",
+    "@react-native-async-storage/async-storage": "^3.0.2"
   },
   "devDependencies": {
     "@changesets/changelog-github": "0.5.2",
     "@changesets/cli": "2.29.8",
     "@rollup/plugin-alias": "^6.0.0",
-    "@rollup/plugin-commonjs": "29.0.0",
+    "@rollup/plugin-commonjs": "29.0.2",
     "@rollup/plugin-json": "^6.1.0",
     "@rollup/plugin-node-resolve": "16.0.3",
     "@types/node": "18.19.122",
     "@types/sinon": "21.0.0",
-    "@typescript-eslint/eslint-plugin": "8.53.0",
-    "@typescript-eslint/parser": "8.53.0",
+    "@typescript-eslint/eslint-plugin": "8.57.2",
+    "@typescript-eslint/parser": "8.57.2",
     "esbuild": "0.25.0",
     "eslint": "8.57.0",
     "eslint-config-prettier": "10.1.8",
     "eslint-config-standard": "^17.1.0",
     "eslint-plugin-import": "^2.31.0",
     "eslint-plugin-n": "^16.0.2",
-    "eslint-plugin-node": "11.1.0",
     "eslint-plugin-prettier": "5.5.5",
     "eslint-plugin-promise": "^6.0.0",
     "eslint-plugin-react": "7.37.5",
-    "eslint-plugin-standard": "4.1.0",
-    "lerna": "9.0.5",
-    "prettier": "3.8.0",
-    "rollup": "4.59.0",
+    "lerna": "^9.0.7",
+    "prettier": "3.8.1",
+    "rollup": "4.60.1",
     "rollup-plugin-esbuild": "6.2.1",
     "rollup-plugin-visualizer": "5.14.0",
-    "sinon": "21.0.1",
+    "sinon": "21.0.3",
     "typescript": "5.9.3",
     "vitest": "3.2.4"
   }
```

### packages/core/package.json
```diff
@@ -53,7 +53,7 @@
     "@walletconnect/types": "2.23.9",
     "@walletconnect/utils": "2.23.9",
     "@walletconnect/window-getters": "1.0.1",
-    "es-toolkit": "1.44.0",
+    "es-toolkit": "1.45.1",
     "events": "3.3.0",
     "uint8arrays": "3.1.1"
   },
```

### packages/sign-client/package.json
```diff
@@ -48,8 +48,6 @@
   },
   "dependencies": {
     "@walletconnect/core": "2.23.9",
-    "@walletconnect/events": "1.0.1",
-    "@walletconnect/heartbeat": "1.2.2",
     "@walletconnect/jsonrpc-utils": "1.0.8",
     "@walletconnect/logger": "3.0.2",
     "@walletconnect/time": "1.0.2",
```

### providers/ethereum-provider/package.json
```diff
@@ -45,8 +45,7 @@
     "prettier": "prettier --check '{src,test}/**/*.{js,ts,jsx,tsx}'"
   },
   "dependencies": {
-    "@reown/appkit": "1.8.17-wc-circular-dependencies-fix.0",
-    "@walletconnect/jsonrpc-http-connection": "1.0.8",
+    "@reown/appkit": "1.8.19",
     "@walletconnect/jsonrpc-provider": "1.0.14",
     "@walletconnect/jsonrpc-types": "1.0.4",
     "@walletconnect/jsonrpc-utils": "1.0.8",
@@ -55,7 +54,6 @@
     "@walletconnect/types": "2.23.9",
     "@walletconnect/universal-provider": "2.23.9",
     "@walletconnect/utils": "2.23.9",
-    "@walletconnect/logger": "3.0.2",
     "events": "3.3.0"
   },
   "devDependencies": {
```

### providers/universal-provider/package.json
```diff
@@ -51,14 +51,14 @@
     "@walletconnect/sign-client": "2.23.9",
     "@walletconnect/types": "2.23.9",
     "@walletconnect/utils": "2.23.9",
-    "es-toolkit": "1.44.0",
+    "es-toolkit": "1.45.1",
     "events": "3.3.0"
   },
   "devDependencies": {
     "ethers": "6.16.0",
     "hardhat": "^3.1.4",
     "uint8arrays": "3.1.1",
-    "wait-on": "9.0.1",
+    "wait-on": "9.0.4",
     "web3": "4.16.0"
   },
   "publishConfig": {
```
