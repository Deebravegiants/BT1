# [?] chore: fix security vulnerabilities and migrate rollup 2 to 4

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-03-02
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/44d591d7a13898605707676089794ac487087eba
Type: security-commit

## Details
chore: fix security vulnerabilities and migrate rollup 2 to 4

Resolve all critical and high npm audit vulnerabilities:
- Update @aws-sdk/client-cloudwatch 3.971.0 -> 3.1000.0
- Update lerna 9.0.3 -> 9.0.5
- Add overrides for tar, axios, minimatch, @isaacs/brace-expansion,
  fast-xml-parser to patch transitive vulnerabilities

Migrate build tooling from Rollup 2 to Rollup 4:
- Update rollup 2.79.2 -> 4.59.0
- Update @rollup/plugin-commonjs 22 -> 29, plugin-node-resolve 13 -> 16,
  plugin-alias 5 -> 6, rollup-plugin-esbuild 4 -> 6
- Fix rollup-plugin-visualizer import (default -> named export)
- Add `with { type: "json" }` to JSON imports in per-package configs
- Add .js extensions to relative imports for Node.js ESM compatibility
- Replace __dirname with import.meta.url in ethereum-provider config

Made-with: Cursor

## Patch
### package.json
```diff
@@ -56,17 +56,20 @@
     "url": "https://github.com/walletconnect/walletconnect-monorepo/issues"
   },
   "overrides": {
-    "tar": "^7.5.7",
+    "tar": "^7.5.8",
     "lodash": "^4.17.23",
-    "vite": "^7.3.1"
+    "vite": "^7.3.1",
+    "axios": "^1.13.5",
+    "minimatch": ">=3.1.4",
+    "@isaacs/brace-expansion": "^5.0.1"
   },
   "devDependencies": {
     "@changesets/changelog-github": "0.5.2",
     "@changesets/cli": "2.29.8",
-    "@rollup/plugin-alias": "^5.1.1",
-    "@rollup/plugin-commonjs": "22.0.2",
+    "@rollup/plugin-alias": "^6.0.0",
+    "@rollup/plugin-commonjs": "29.0.0",
     "@rollup/plugin-json": "^6.1.0",
-    "@rollup/plugin-node-resolve": "13.3.0",
+    "@rollup/plugin-node-resolve": "16.0.3",
     "@types/node": "18.19.122",
     "@types/sinon": "21.0.0",
     "@typescript-eslint/eslint-plugin": "8.53.0",
@@ -82,10 +85,10 @@
     "eslint-plugin-promise": "^6.0.0",
     "eslint-plugin-react": "7.37.5",
     "eslint-plugin-standard": "4.1.0",
-    "lerna": "9.0.3",
+    "lerna": "9.0.5",
     "prettier": "3.8.0",
-    "rollup": "2.79.2",
-    "rollup-plugin-esbuild": "4.9.3",
+    "rollup": "4.59.0",
+    "rollup-plugin-esbuild": "6.2.1",
     "rollup-plugin-visualizer": "5.14.0",
     "sinon": "21.0.1",
     "typescript": "5.9.3",
```

### packages/core/rollup.config.js
```diff
@@ -1,4 +1,4 @@
-import { name, dependencies } from "./package.json";
-import createConfig from "../../rollup.config";
+import pkg from "./package.json" with { type: "json" };
+import createConfig from "../../rollup.config.js";
 
-export default createConfig(name, Object.keys(dependencies));
+export default createConfig(pkg.name, Object.keys(pkg.dependencies));
```

### packages/pay/rollup.config.js
```diff
@@ -1,4 +1,4 @@
-import { name, dependencies } from "./package.json";
+import pkg from "./package.json" with { type: "json" };
 import createConfig from "../../rollup.config.js";
 
-export default createConfig(name, Object.keys(dependencies));
+export default createConfig(pkg.name, Object.keys(pkg.dependencies));
```

### packages/pos-client/rollup.config.js
```diff
@@ -1,4 +1,4 @@
-import { name, dependencies } from "./package.json";
+import pkg from "./package.json" with { type: "json" };
 import createConfig from "../../rollup.config.js";
 
-export default createConfig(name, Object.keys(dependencies));
+export default createConfig(pkg.name, Object.keys(pkg.dependencies));
```

### packages/sign-client/package.json
```diff
@@ -58,7 +58,7 @@
     "events": "3.3.0"
   },
   "devDependencies": {
-    "@aws-sdk/client-cloudwatch": "3.971.0",
+    "@aws-sdk/client-cloudwatch": "3.1000.0",
     "ethers": "6.16.0"
   },
   "repository": {
```

### packages/sign-client/rollup.config.js
```diff
@@ -1,4 +1,4 @@
-import { name, dependencies } from "./package.json";
-import createConfig from "../../rollup.config";
+import pkg from "./package.json" with { type: "json" };
+import createConfig from "../../rollup.config.js";
 
-export default createConfig(name, Object.keys(dependencies));
+export default createConfig(pkg.name, Object.keys(pkg.dependencies));
```

### packages/types/rollup.config.js
```diff
@@ -1,4 +1,4 @@
-import { name, dependencies } from "./package.json";
-import createConfig from "../../rollup.config";
+import pkg from "./package.json" with { type: "json" };
+import createConfig from "../../rollup.config.js";
 
-export default createConfig(name, Object.keys(dependencies));
+export default createConfig(pkg.name, Object.keys(pkg.dependencies));
```

### packages/utils/rollup.config.js
```diff
@@ -1,4 +1,4 @@
-import { name, dependencies } from "./package.json";
-import createConfig from "../../rollup.config";
+import pkg from "./package.json" with { type: "json" };
+import createConfig from "../../rollup.config.js";
 
-export default createConfig(name, Object.keys(dependencies));
+export default createConfig(pkg.name, Object.keys(pkg.dependencies));
```

### providers/ethereum-provider/package.json
```diff
@@ -61,7 +61,7 @@
   "devDependencies": {
     "hardhat": "^3.1.4",
     "ethers": "6.16.0",
-    "@rollup/plugin-alias": "^5.1.1",
+    "@rollup/plugin-alias": "^6.0.0",
     "uint8arrays": "3.1.1",
     "web3": "4.16.0"
   },
```

### providers/ethereum-provider/rollup.config.js
```diff
@@ -1,23 +1,23 @@
-import { name, dependencies, peerDependencies } from "./package.json";
-import createConfig, { input, plugins } from "../../rollup.config";
+import pkg from "./package.json" with { type: "json" };
+import createConfig, { input, plugins } from "../../rollup.config.js";
 import alias from "@rollup/plugin-alias";
-import path from "path";
+import { fileURLToPath } from "node:url";
+import path from "node:path";
+
+const __dirname = path.dirname(fileURLToPath(import.meta.url));
 
-// `ethereum-provider` has dynamic imports, so we need to enable inlineDynamicImports
 const options = { inlineDynamicImports: true };
 
-// keep `@reown/appkit/core` in the external dependencies, else the builds will balloon in size
-const externalDependencies = Object.keys({ ...dependencies, ...peerDependencies }).concat(
+const externalDependencies = Object.keys({ ...pkg.dependencies, ...pkg.peerDependencies }).concat(
   "@reown/appkit/core",
 );
-export default createConfig(name, externalDependencies, options, options, options, [
+export default createConfig(pkg.name, externalDependencies, options, options, options, [
   {
     input,
     plugins: [
       alias({
         entries: [
           {
-            // this config allows separate files to be used for the browser and native builds
             find: "./utils/appkit",
             replacement: path.resolve(__dirname, `src/utils/appkit.native.ts`),
           },
@@ -30,7 +30,7 @@ export default createConfig(name, externalDependencies, options, options, option
       file: "./dist/index.native.js",
       format: "cjs",
       exports: "named",
-      name,
+      name: pkg.name,
       sourcemap: true,
       ...options,
     },
```

### providers/signer-connection/rollup.config.js
```diff
@@ -1,4 +1,4 @@
-import { name, dependencies } from "./package.json";
-import createConfig from "../../rollup.config";
+import pkg from "./package.json" with { type: "json" };
+import createConfig from "../../rollup.config.js";
 
-export default createConfig(name, Object.keys(dependencies));
+export default createConfig(pkg.name, Object.keys(pkg.dependencies));
```
