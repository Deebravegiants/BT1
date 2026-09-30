# [?] [Snyk] Fix for 2 vulnerabilities (#6598)

## Summary
Severity: Unknown
Chain: Tooling
Component: web3/web3.js
Published: 2023-11-16
Source: https://github.com/web3/web3.js/commit/2c132c5c6365e1bc16ac1e0bbcf82795df10ee26
Type: security-commit

## Details
[Snyk] Fix for 2 vulnerabilities (#6598)

* fix: docs/package.json & docs/yarn.lock to reduce vulnerabilities

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-JS-AXIOS-6032459
- https://snyk.io/vuln/SNYK-JS-GOT-2932019

* update to node 18 at Docs CloudFlare Deploy

* tiny fixes at docs mark down

* update some docs dependencies

---------

Co-authored-by: snyk-bot <snyk-bot@snyk.io>

## Patch
### .github/workflows/deploy-docs.yaml
```diff
@@ -15,7 +15,7 @@ jobs:
           - uses: actions/setup-node@v3
             with:
               cache: yarn
-              node-version: '16'
+              node-version: '18'
           - run: yarn install --frozen-lockfile
           - run: yarn run build:docs
           - name: Publish to Cloudflare Pages
```

### docs/docs/guides/web3_plugin_guide/plugin_users.md
```diff
@@ -10,7 +10,7 @@ import TabItem from '@theme/TabItem';
 
 This guide intends to provide the necessary context for registering plugins with web3.js packages.
 
-To help you get started, take a look at a list of useful plugins at <https://web3js.org/plugins>
+To help you get started, take a look at a list of useful plugins at [https://web3js.org/plugins](https://web3js.org/plugins)
 
 ## Installing the Plugin
 
```

### docs/docusaurus.config.js
```diff
@@ -15,8 +15,8 @@ You should have received a copy of the GNU Lesser General Public License
 along with web3.js.  If not, see <http://www.gnu.org/licenses/>.
 */
 
-const lightCodeTheme = require('prism-react-renderer/themes/github');
-const darkCodeTheme = require('prism-react-renderer/themes/dracula');
+const lightCodeTheme = require('prism-react-renderer').themes.github;
+const darkCodeTheme = require('prism-react-renderer').themes.dracula;
 const { join } = require('path');
 
 const packages = [
@@ -65,7 +65,7 @@ const config = {
 	plugins: [
 		'@docusaurus/theme-live-codeblock',
 		[
-			'@mpetrunic/docusaurus-plugin-typedoc-api',
+			'docusaurus-plugin-typedoc-api',
 			{
 				projectRoot: join(__dirname, '..'),
 				// Monorepo
```

### docs/package.json
```diff
@@ -15,21 +15,21 @@
 		"typecheck": "tsc"
 	},
 	"dependencies": {
-		"@docusaurus/core": "^2.4.3",
-		"@docusaurus/preset-classic": "^2.4.3",
-		"@docusaurus/theme-live-codeblock": "^2.4.3",
-		"@mdx-js/react": "^1.6.22",
+		"@docusaurus/core": "^3.0.0",
+		"@docusaurus/preset-classic": "^3.0.0",
+		"@docusaurus/theme-live-codeblock": "^3.0.0",
+		"@mdx-js/react": "^3.0.0",
 		"classnames": "^2.3.2",
 		"clsx": "^2.0.0",
-		"docusaurus-lunr-search": "^3.2.0",
-		"prism-react-renderer": "^1.3.1",
+		"docusaurus-lunr-search": "^3.3.0",
+		"prism-react-renderer": "^2.2.0",
 		"react": "^18.2.0",
 		"react-dom": "^18.2.0"
 	},
 	"devDependencies": {
-		"@docusaurus/module-type-aliases": "^2.4.3",
-		"@mpetrunic/docusaurus-plugin-typedoc-api": "^3.0.0",
-		"@tsconfig/docusaurus": "^1.0.7",
+		"@docusaurus/module-type-aliases": "^3.0.0",
+		"@tsconfig/docusaurus": "^2.0.2",
+		"docusaurus-plugin-typedoc-api": "^4.0.1",
 		"typescript": "^4.6.4"
 	},
 	"browserslist": {
```

### packages/web3-eth-contract/CHANGELOG.md
```diff
@@ -13,9 +13,12 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 The receiptInfo Status will now be be an unsigned integer instead of boolean value to comply with the specification.
 
-<https://github.com/ethereum/execution-apis/blob/773ffd230ae5cd037e32415855cf8d4f1e729b2d/src/schemas/receipt.yaml#L94-L97>
+[https://github.com/ethereum/execution-apis/blob/773ffd230ae5cd037e32415855cf8d4f1e729b2d/src/schemas/receipt.yaml#L94-L97](https://github.com/ethereum/execution-apis/blob/773ffd230ae5cd037e32415855cf8d4f1e729b2d/src/schemas/receipt.yaml#L94-L97)
 
-<details><summary>1.x</summary>
+<details>
+<summary>
+1.x
+</summary>
 <p>
 
 ```ts
@@ -30,7 +33,9 @@ myContract.methods
 </p>
 </details>
 
-<details><summary>4.x</summary>
+<details><summary>
+4.x
+</summary>
 <p>
 
 ```ts
@@ -51,7 +56,9 @@ myContract.methods
 
 In 1.x when following was executed `deploy().send().on(‘sending’, payload => {})`. The `payload` was the complete the JSON-RPC Payload. In 4.x it will just be the transaction which is about to be transmitted. Earlier it was accessible by from `payload.params[0]`, now will be available directly to event handler.
 
-<details><summary>1.x</summary>
+<details><summary>
+1.x
+</summary>
 <p>
 
 ```ts
@@ -67,7 +74,9 @@ myContract
 </p>
 </details>
 
-<details><summary>4.x</summary>
+<details><summary>
+4.x
+</summary>
 <p>
 
 ```ts
@@ -87,7 +96,9 @@ myContract
 
 In 1.x, the `confirmations` handler was invoked with multiple parameters. But in `4.x` there will be one parameter as object but with all the same properties.
 
-<details><summary>1.x</summary>
+<details><summary>
+1.x
+</summary>
 <p>
 
 ```ts
@@ -97,7 +108,9 @@ myContract .send().on(‘confirmation’, (confirmations: number, receipt: objec
 </p>
 </details>
 
-<details><summary>4.x</summary>
+<details><summary>
+4.x
+</summary>
 <p>
 
 ```ts
@@ -118,7 +131,9 @@ myContract .send().on(‘confirmation’, ({confirmations: bigint, receipt: obje
 
 The error message will be different if you try to create a contract object without a `new` keyword.
 
-<details><summary>1.x</summary>
+<details><summary>
+1.x
+</summary>
 <p>
 
 ```ts
@@ -128,7 +143,9 @@ Please use the "new" keyword to instantiate a web3.eth.Contract() object!
 </p>
 </details>
 
-<details><summary>4.x</summary>
+<details><summary>
+4.x
+</summary>
 <p>
 
 ```ts
@@ -150,7 +167,9 @@ In `4.x` you will not get any warning. But `toBlock` still have no effect.
 
 In `1.x` the contract `.send` method was always resolved with `transactionHash`. That enforces user to make an extra call to get any further information. In `4.x` the `.send` function will resolve with `receipt` object.
 
-<details><summary>1.x</summary>
+<details><summary>
+1.x
+</summary>
 <p>
 
 ```ts
@@ -160,7 +179,9 @@ const transactionHash = await myContract.method.MyMethod().send();
 </p>
 </details>
 
-<details><summary>4.x</summary>
+<details><summary>
+4.x
+</summary>
 <p>
 
 ```ts
```

### packages/web3-validator/CHANGELOG.md
```diff
@@ -153,7 +153,7 @@ Documentation:
 
 -   Multi-dimensional arrays are now handled properly when parsing ABIs (#6435)
 -   Fix issue with default config with babel (and React): "TypeError: Cannot convert a BigInt value to a number #6187" (#6506)
--   Validator will now properly handle all valid numeric type sizes: intN / uintN where 8 <= N <= 256 and N % 8 == 0 (#6434)
+-   Validator will now properly handle all valid numeric type sizes: intN / uintN where 8 < = N < = 256 and N % 8 == 0 (#6434)
 -   Will now throw SchemaFormatError when unsupported format is passed to `convertToZod` method (#6434)
 
 ## [Unreleased]
\ No newline at end of file
```
