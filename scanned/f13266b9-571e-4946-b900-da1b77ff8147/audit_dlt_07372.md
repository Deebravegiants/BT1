# [?] fix: Upgrade Storybook to 7.6.21 to patch security vulnerability (#38979)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2025-12-19
Source: https://github.com/MetaMask/metamask-extension/commit/a41bc07d63347af44af483a120d22792ccbb60d6
Type: security-commit

## Details
fix: Upgrade Storybook to 7.6.21 to patch security vulnerability (#38979)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**

This PR upgrades Storybook from version 7.6.20 to 7.6.21 to patch a
security vulnerability affecting versions 7.0.0-10.1.9.

**What is the reason for the change?**
Storybook has a security vulnerability (CVE) where environment variables
from `.env` files could be unexpectedly bundled into publicly viewable
Storybook artifacts when specific code patterns are used. While our
initial investigation shows no current credential exposure in the
deployed Storybook, upgrading prevents future accidental exposure.

**What is the improvement/solution?**
- Upgraded all `@storybook/*` packages from `^7.6.20` to `^7.6.21`
- Upgraded `storybook` package from `^7.6.20` to `^7.6.21`
- Added `@storybook/*` and `storybook` to `npmPreapprovedPackages` in
`.yarnrc.yml` to bypass the 3-day age gate for this security patch

**Security Advisory:** https://storybook.js.org/blog/security-advisory/

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/38979?quickstart=1)

## **Changelog**

CHANGELOG entry: null

## **Related issues**

Fixes: Security vulnerability in Storybook 7.6.20 (CVE - environment
variable exposure)

## **Manual testing steps**

1. Pull this branch
2. Run `yarn install` to install updated dependencies
3. Run `yarn storybook` to start Storybook development server
4. Verify Storybook loads without errors
5. Verify existing stories render correctly
6. Run `yarn storybook:build` to verify production build succeeds

## **Screenshots/Recordings**

Not applicable - this is a dependency version upgrade with no visual
changes.

### **Before**

Storybook version: 7.6.20 (vulnerable to environment variable exposure)

### **After**

Storybook version: 7.6.21 (patched) still works as expected


https://github.com/user-attachments/assets/37955cbb-030a-4e29-8c10-68f2400a949b


## **Pre-merge author checklist**

- [x] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [x] I've completed the PR template to the best of my ability
- [x] I've included tests if applicable (N/A - dependency upgrade)
- [x] I've documented my code using [JSDoc](https://jsdoc.app/) format
if applicable (N/A - no code changes)
- [ ] I've applied the right labels on the PR (see [labeling
guidelines](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/LABELING_GUIDELINES.md)).
Not required for external contributors.

## **Pre-merge reviewer checklist**

- [ ] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [ ] I've confirm that this PR addresses all acceptance criteria
described in the ticket it closes and includes the necessary testing
evidence such as recordings and or screenshots.

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Upgrades all Storybook-related dependencies from 7.6.20 to 7.6.21.
> 
> - **Dependencies**
> - **Storybook ecosystem**: Bump `@storybook/*` and `storybook` from
`7.6.20` to `7.6.21` in `package.json`.
>   - Update `yarn.lock` to reflect the new Storybook versions.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
ae991b16c93bfc9f1f83ae4f57e8a0f24ec1aef1. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Patch
### package.json
```diff
@@ -522,19 +522,19 @@
     "@sentry/cli": "^2.56.0",
     "@slack/types": "^2.14.0",
     "@slack/webhook": "^7.0.5",
-    "@storybook/addon-a11y": "^7.6.20",
-    "@storybook/addon-actions": "^7.6.20",
-    "@storybook/addon-docs": "^7.6.20",
-    "@storybook/addon-essentials": "^7.6.20",
-    "@storybook/addons": "^7.6.20",
-    "@storybook/api": "^7.6.20",
-    "@storybook/client-api": "^7.6.20",
-    "@storybook/components": "^7.6.20",
-    "@storybook/react": "^7.6.20",
-    "@storybook/react-webpack5": "^7.6.20",
+    "@storybook/addon-a11y": "^7.6.21",
+    "@storybook/addon-actions": "^7.6.21",
+    "@storybook/addon-docs": "^7.6.21",
+    "@storybook/addon-essentials": "^7.6.21",
+    "@storybook/addons": "^7.6.21",
+    "@storybook/api": "^7.6.21",
+    "@storybook/client-api": "^7.6.21",
+    "@storybook/components": "^7.6.21",
+    "@storybook/react": "^7.6.21",
+    "@storybook/react-webpack5": "^7.6.21",
     "@storybook/storybook-deployer": "^2.8.16",
     "@storybook/test-runner": "^0.14.1",
-    "@storybook/theming": "^7.6.20",
+    "@storybook/theming": "^7.6.21",
     "@swc/helpers": "^0.5.17",
     "@testing-library/dom": "^10.4.0",
     "@testing-library/jest-dom": "^6.6.3",
@@ -714,7 +714,7 @@
     "source-map": "^0.7.4",
     "source-map-explorer": "^2.4.2",
     "sprintf-js": "^1.1.3",
-    "storybook": "^7.6.20",
+    "storybook": "^7.6.21",
     "stream-browserify": "^3.0.0",
     "stream-http": "^3.2.0",
     "string.prototype.matchall": "^4.0.2",
```

### yarn.lock
```diff
@@ -13066,188 +13066,188 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@storybook/addon-a11y@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-a11y@npm:7.6.20"
+"@storybook/addon-a11y@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-a11y@npm:7.6.21"
   dependencies:
-    "@storybook/addon-highlight": "npm:7.6.20"
+    "@storybook/addon-highlight": "npm:7.6.21"
     axe-core: "npm:^4.2.0"
-  checksum: 10/4da3479a6db035092d6ef59dfd4465357976623db9ff84b9178dd30210e63f728d9f2819850fdfcd6fe00739b3849d4399255e90917ac6083c37ece97d4da30a
+  checksum: 10/706ebdc01983beb46ba6a0b60cbf67e015f8f88848fe9a7d246b74db37a4f432dfb1c100099cf0357c5b78945d9ae1eb9b85b7217180568c8fc7937539dcad89
   languageName: node
   linkType: hard
 
-"@storybook/addon-actions@npm:7.6.20, @storybook/addon-actions@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-actions@npm:7.6.20"
+"@storybook/addon-actions@npm:7.6.21, @storybook/addon-actions@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-actions@npm:7.6.21"
   dependencies:
-    "@storybook/core-events": "npm:7.6.20"
+    "@storybook/core-events": "npm:7.6.21"
     "@storybook/global": "npm:^5.0.0"
     "@types/uuid": "npm:^9.0.1"
     dequal: "npm:^2.0.2"
     polished: "npm:^4.2.2"
     uuid: "npm:^9.0.0"
-  checksum: 10/cbec5ebbb8a4a632a14b04c0ae32adc4d9783ecc3faba325ede0e172170b579ffd8e5d7c825a1cd61a1008ed69fc78eda7c63df58490c543534f63318683d4b9
+  checksum: 10/13bcd833fcf87ac2869d8c0aa4a4aec1a77dc991778ce0d3e98d593c53b745ae26da0ee3198a205be4b930f6cb74549a13d8bf47196d6e6f27e4f8a4a6ee73d4
   languageName: node
   linkType: hard
 
-"@storybook/addon-backgrounds@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-backgrounds@npm:7.6.20"
+"@storybook/addon-backgrounds@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-backgrounds@npm:7.6.21"
   dependencies:
     "@storybook/global": "npm:^5.0.0"
     memoizerific: "npm:^1.11.3"
     ts-dedent: "npm:^2.0.0"
-  checksum: 10/458c9493fb8f8efe552efd4a3f4f3a1c3fc0bee539c508de92da6af7efd3fde047d0fce40521bf8b9453747b7c9f07352483500cef173fb8ee382817e2ec692e
+  checksum: 10/67e330f2e81f93209d841de14f120911555395000e870088c7ad4c881a3b41b35832d6b97300344497abee95c088dbf6391ac2b39be260947eb67c3346122b93
   languageName: node
   linkType: hard
 
-"@storybook/addon-controls@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-controls@npm:7.6.20"
+"@storybook/addon-controls@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-controls@npm:7.6.21"
   dependencies:
-    "@storybook/blocks": "npm:7.6.20"
+    "@storybook/blocks": "npm:7.6.21"
     lodash: "npm:^4.17.21"
     ts-dedent: "npm:^2.0.0"
-  checksum: 10/27b0f4d5e751445c16e1a86de4013ee8d60136cc040914cc8e7a9cc53ca93084094335d4bc78fa74cb566d38ce519d5a5dd3cd7f4985cc4c2062f70ad9ebe3b9
+  checksum: 10/f2a1640cd54e7aa074d823e746765c120045936c1031357ff1f5a2b62e7ef73daa719d3e959292c0eff7212581daa98ec5ed7975a38f8f5048904226d1483aaf
   languageName: node
   linkType: hard
 
-"@storybook/addon-docs@npm:7.6.20, @storybook/addon-docs@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-docs@npm:7.6.20"
+"@storybook/addon-docs@npm:7.6.21, @storybook/addon-docs@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-docs@npm:7.6.21"
   dependencies:
     "@jest/transform": "npm:^29.3.1"
     "@mdx-js/react": "npm:^2.1.5"
-    "@storybook/blocks": "npm:7.6.20"
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/components": "npm:7.6.20"
-    "@storybook/csf-plugin": "npm:7.6.20"
-    "@storybook/csf-tools": "npm:7.6.20"
+    "@storybook/blocks": "npm:7.6.21"
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/components": "npm:7.6.21"
+    "@storybook/csf-plugin": "npm:7.6.21"
+    "@storybook/csf-tools": "npm:7.6.21"
     "@storybook/global": "npm:^5.0.0"
     "@storybook/mdx2-csf": "npm:^1.0.0"
-    "@storybook/node-logger": "npm:7.6.20"
-    "@storybook/postinstall": "npm:7.6.20"
-    "@storybook/preview-api": "npm:7.6.20"
-    "@storybook/react-dom-shim": "npm:7.6.20"
-    "@storybook/theming": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/node-logger": "npm:7.6.21"
+    "@storybook/postinstall": "npm:7.6.21"
+    "@storybook/preview-api": "npm:7.6.21"
+    "@storybook/react-dom-shim": "npm:7.6.21"
+    "@storybook/theming": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     fs-extra: "npm:^11.1.0"
     remark-external-links: "npm:^8.0.0"
     remark-slug: "npm:^6.0.0"
     ts-dedent: "npm:^2.0.0"
   peerDependencies:
     react: ^16.8.0 || ^17.0.0 || ^18.0.0
     react-dom: ^16.8.0 || ^17.0.0 || ^18.0.0
-  checksum: 10/04b162f169f2d203089a04a522f5c7923f856e6708fb5da5509ba075abea000dac9fdb4e198bcb0f0b58dd31b79a67126fe1ced210fce6193c3c6b6c4f0123ff
-  languageName: node
-  linkType: hard
-
-"@storybook/addon-essentials@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-essentials@npm:7.6.20"
-  dependencies:
-    "@storybook/addon-actions": "npm:7.6.20"
-    "@storybook/addon-backgrounds": "npm:7.6.20"
-    "@storybook/addon-controls": "npm:7.6.20"
-    "@storybook/addon-docs": "npm:7.6.20"
-    "@storybook/addon-highlight": "npm:7.6.20"
-    "@storybook/addon-measure": "npm:7.6.20"
-    "@storybook/addon-outline": "npm:7.6.20"
-    "@storybook/addon-toolbars": "npm:7.6.20"
-    "@storybook/addon-viewport": "npm:7.6.20"
-    "@storybook/core-common": "npm:7.6.20"
-    "@storybook/manager-api": "npm:7.6.20"
-    "@storybook/node-logger": "npm:7.6.20"
-    "@storybook/preview-api": "npm:7.6.20"
+  checksum: 10/069a29350bed5d853372d86f7169f49a680eb55d49cde1bd968e7781295c551b8c99c447f1a9d5fbce510e2ec6df9c9b2a8e431501023a8d1955aea3d318ecd1
+  languageName: node
+  linkType: hard
+
+"@storybook/addon-essentials@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-essentials@npm:7.6.21"
+  dependencies:
+    "@storybook/addon-actions": "npm:7.6.21"
+    "@storybook/addon-backgrounds": "npm:7.6.21"
+    "@storybook/addon-controls": "npm:7.6.21"
+    "@storybook/addon-docs": "npm:7.6.21"
+    "@storybook/addon-highlight": "npm:7.6.21"
+    "@storybook/addon-measure": "npm:7.6.21"
+    "@storybook/addon-outline": "npm:7.6.21"
+    "@storybook/addon-toolbars": "npm:7.6.21"
+    "@storybook/addon-viewport": "npm:7.6.21"
+    "@storybook/core-common": "npm:7.6.21"
+    "@storybook/manager-api": "npm:7.6.21"
+    "@storybook/node-logger": "npm:7.6.21"
+    "@storybook/preview-api": "npm:7.6.21"
     ts-dedent: "npm:^2.0.0"
   peerDependencies:
     react: ^16.8.0 || ^17.0.0 || ^18.0.0
     react-dom: ^16.8.0 || ^17.0.0 || ^18.0.0
-  checksum: 10/caa019515d0cf6b628a13611d231145254ca4c69aa01de78f597aef32425cdd1b227ec916f45e56ccf30790503e552adc931d44cb1e76e11a24a19378638bfdd
+  checksum: 10/c8a31990e0e519b9e6383cd5917e293f8e37815cf06bc81c9884794e97c57b4aed074b00a91791f87ee01eea6370db8df434d1bb63e52bc87803d91a4961881a
   languageName: node
   linkType: hard
 
-"@storybook/addon-highlight@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-highlight@npm:7.6.20"
+"@storybook/addon-highlight@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-highlight@npm:7.6.21"
   dependencies:
     "@storybook/global": "npm:^5.0.0"
-  checksum: 10/80258b39b9611c633ee131424af7694addaf66cc4b39e120202634ac30c401d1b654662e8d2677151743e10cf21b5711fe8c2f7a4e695c994240e4ad84251d5b
+  checksum: 10/72628350ebb0e7c520bef1348613a78762f0c95ef69241dfcf6811bf98cef2d451ef4455c96057f4c7e87ae054bb4848fcb001a483de9d84c3183c0876aa4235
   languageName: node
   linkType: hard
 
-"@storybook/addon-measure@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-measure@npm:7.6.20"
+"@storybook/addon-measure@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-measure@npm:7.6.21"
   dependencies:
     "@storybook/global": "npm:^5.0.0"
     tiny-invariant: "npm:^1.3.1"
-  checksum: 10/ef2db439402bd8710513ecfb1ecf47d3572e93229d6a41287a8114fc714039387ef3562ddb5a4f1a9930a96587073e59975a87f47cf45c90d0deb7052662cf82
+  checksum: 10/f8487ac65956214e958a8a8de9fbc1c787736cac9739abf1bd5f40cc9e76827b8859aa6cc2665e72c6907d1503c8371713383abe1eee5310d96da3a0dab69950
   languageName: node
   linkType: hard
 
-"@storybook/addon-outline@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-outline@npm:7.6.20"
+"@storybook/addon-outline@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-outline@npm:7.6.21"
   dependencies:
     "@storybook/global": "npm:^5.0.0"
     ts-dedent: "npm:^2.0.0"
-  checksum: 10/74cf0cde404f883c1dfdda64036d90dc0174ab742d9f81c8a88fc1c131230aec494236bdd8fa00e0ac7e0e4d153de54bdfe6ef55733d775932f5f62ee8239775
+  checksum: 10/40f853a17543e763bfdff4e33407daa2966dc1a929d814ecfdafa169dc3b63e7a11c923231dfebf7b8f889eba962d9e1945e220a9599663a20fa6c3f901d3654
   languageName: node
   linkType: hard
 
-"@storybook/addon-toolbars@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-toolbars@npm:7.6.20"
-  checksum: 10/3338badd22714001ba022a9d41a3bf7d9e178fdf26652914b09b7cfb3ed2cd6e680360d8b9f667ae8043c215d009965b119fd4918676f2ebeafc888eec5310a3
+"@storybook/addon-toolbars@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-toolbars@npm:7.6.21"
+  checksum: 10/e2db2cb1fc56ed25c90d270b1b42dd71fd8079e6e10c2560e1d1a0adf6c1992b4d12646e4df4f8db1d40e899dc3ca7597acdbd052603903090019039afd31b51
   languageName: node
   linkType: hard
 
-"@storybook/addon-viewport@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addon-viewport@npm:7.6.20"
+"@storybook/addon-viewport@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addon-viewport@npm:7.6.21"
   dependencies:
     memoizerific: "npm:^1.11.3"
-  checksum: 10/aba68c9de68d61e7b915909ba6296e9091e8be48d193ac3f84acebf7488bf96ee1e754f6b2a3728765d15d3ecef491531130246f9e9a08b395c21f88ef584043
+  checksum: 10/358877a430e577f70b9792c950cb3b9fbf3f3d4ec2382e35454809956f396705ae9b254b7ed85f0fd64762ffe82834e60f204e10c469de11a7dd598505897fe4
   languageName: node
   linkType: hard
 
-"@storybook/addons@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/addons@npm:7.6.20"
+"@storybook/addons@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/addons@npm:7.6.21"
   dependencies:
-    "@storybook/manager-api": "npm:7.6.20"
-    "@storybook/preview-api": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
-  checksum: 10/801b8281b6e7b6f96808c83c8f862da86d9bb3f5e1abf57a0f51ba4b46b1530613b869a9660147115ebc7787e0bf01eb10b92516c608da0cd6e83e6bf74a2e9c
+    "@storybook/manager-api": "npm:7.6.21"
+    "@storybook/preview-api": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
+  checksum: 10/a311605e02c7026aa2c15a12c2b0548f56a041283dc9291e1bf2424f658e7d50423131ebb300cde2d35ea4e0500614e7a4dde40fd8aee897e502e35c430da976
   languageName: node
   linkType: hard
 
-"@storybook/api@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/api@npm:7.6.20"
+"@storybook/api@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/api@npm:7.6.21"
   dependencies:
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/manager-api": "npm:7.6.20"
-  checksum: 10/2aeabb07d1d245c4a3500dec8dd2472e0f0e6f81c06d1bdcc81f79e9a416c3ddb91b98a72449d8857a26177532bfc93f8094918ef047284c971075062d713630
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/manager-api": "npm:7.6.21"
+  checksum: 10/16e9b66fefde4ad4d6f1727e53ef4622cdd123c0b21e9e7d19dcc97ea390d1f07865b40890b3a601f67a9ae477f126d14f822507c8ffd83add15bf7b23514a8d
   languageName: node
   linkType: hard
 
-"@storybook/blocks@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/blocks@npm:7.6.20"
+"@storybook/blocks@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/blocks@npm:7.6.21"
   dependencies:
-    "@storybook/channels": "npm:7.6.20"
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/components": "npm:7.6.20"
-    "@storybook/core-events": "npm:7.6.20"
+    "@storybook/channels": "npm:7.6.21"
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/components": "npm:7.6.21"
+    "@storybook/core-events": "npm:7.6.21"
     "@storybook/csf": "npm:^0.1.2"
-    "@storybook/docs-tools": "npm:7.6.20"
+    "@storybook/docs-tools": "npm:7.6.21"
     "@storybook/global": "npm:^5.0.0"
-    "@storybook/manager-api": "npm:7.6.20"
-    "@storybook/preview-api": "npm:7.6.20"
-    "@storybook/theming": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/manager-api": "npm:7.6.21"
+    "@storybook/preview-api": "npm:7.6.21"
+    "@storybook/theming": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     "@types/lodash": "npm:^4.14.167"
     color-convert: "npm:^2.0.1"
     dequal: "npm:^2.0.2"
@@ -13263,18 +13263,18 @@ __metadata:
   peerDependencies:
     react: ^16.8.0 || ^17.0.0 || ^18.0.0
     react-dom: ^16.8.0 || ^17.0.0 || ^18.0.0
-  checksum: 10/fa893dbf5600b48bdcea757e844f2fc70ab5b68309527802e639c4c596d53c937cc53ec6246afa93ac3da0d83bfb65c50666e66a7c474a776c57fe80a5c7c98f
+  checksum: 10/e041e205182b5b95564b13714c438a841f3d586f99b5c450a7707c7c157c351a15129f19ee0a73cf06e6032af34bdf89ccd3647f5349818813a56bdc013798e3
   languageName: node
   linkType: hard
 
-"@storybook/builder-manager@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/builder-manager@npm:7.6.20"
+"@storybook/builder-manager@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/builder-manager@npm:7.6.21"
   dependencies:
     "@fal-works/esbuild-plugin-global-externals": "npm:^2.1.2"
-    "@storybook/core-common": "npm:7.6.20"
-    "@storybook/manager": "npm:7.6.20"
-    "@storybook/node-logger": "npm:7.6.20"
+    "@storybook/core-common": "npm:7.6.21"
+    "@storybook/manager": "npm:7.6.21"
+    "@storybook/node-logger": "npm:7.6.21"
     "@types/ejs": "npm:^3.1.1"
     "@types/find-cache-dir": "npm:^3.2.1"
     "@yarnpkg/esbuild-plugin-pnp": "npm:^3.0.0-rc.10"
@@ -13287,23 +13287,23 @@ __metadata:
     fs-extra: "npm:^11.1.0"
     process: "npm:^0.11.10"
     util: "npm:^0.12.4"
-  checksum: 10/08e6b1294495bcfdfafa3ce1159785fcf4bc0b7ea2f1cdeb88b8ac952017c6106209617cd01c59c35d4dd74cc61eead3c9746ffca6ccf4e18e9ebf0bbda1c819
+  checksum: 10/065544712f14954337cd6c2d043cb41331413b2154c5eca1d2703c1233bb6280ddfc451a7fd056bd30a33e1a630197f8696945a4b109ccbc0aba519366d27bc2
   languageName: node
   linkType: hard
 
-"@storybook/builder-webpack5@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/builder-webpack5@npm:7.6.20"
+"@storybook/builder-webpack5@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/builder-webpack5@npm:7.6.21"
   dependencies:
     "@babel/core": "npm:^7.23.2"
-    "@storybook/channels": "npm:7.6.20"
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/core-common": "npm:7.6.20"
-    "@storybook/core-events": "npm:7.6.20"
-    "@storybook/core-webpack": "npm:7.6.20"
-    "@storybook/node-logger": "npm:7.6.20"
-    "@storybook/preview": "npm:7.6.20"
-    "@storybook/preview-api": "npm:7.6.20"
+    "@storybook/channels": "npm:7.6.21"
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/core-common": "npm:7.6.21"
+    "@storybook/core-events": "npm:7.6.21"
+    "@storybook/core-webpack": "npm:7.6.21"
+    "@storybook/node-logger": "npm:7.6.21"
+    "@storybook/preview": "npm:7.6.21"
+    "@storybook/preview-api": "npm:7.6.21"
     "@swc/core": "npm:^1.3.82"
     "@types/node": "npm:^18.0.0"
     "@types/semver": "npm:^7.3.4"
@@ -13336,40 +13336,40 @@ __metadata:
   peerDependenciesMeta:
     typescript:
       optional: true
-  checksum: 10/deb645ccb3a3f83172e91450177db4256dac1d35994a7b5d81184065914b084475eda585b718cf7f2e7b6059f20d3a68899b4d4d059d59b765a17c1efff4c3c1
+  checksum: 10/ddbac7bb69812f948867f741c2d4889767d7d099dd41731be4cdf2e1e32f15b0d1a676d71c304e4db6b183bfb0c3a8b92c2078d8fe52a0118a7c1f8f918da1c9
   languageName: node
   linkType: hard
 
-"@storybook/channels@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/channels@npm:7.6.20"
+"@storybook/channels@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/channels@npm:7.6.21"
   dependencies:
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/core-events": "npm:7.6.20"
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/core-events": "npm:7.6.21"
     "@storybook/global": "npm:^5.0.0"
     qs: "npm:^6.10.0"
     telejson: "npm:^7.2.0"
     tiny-invariant: "npm:^1.3.1"
-  checksum: 10/3dc827df9d0d0c0c68f10edbf5169e42c2cdb43832cb14ce3ac8149f295219f8bae6ed27300fd50e6a78080914cf142d1810fdbcf687dd313a7bfac41386cd95
+  checksum: 10/b16421133d07314e7f9aedc460b40cd146edc946489e14d563adae42fcf4257d03806b949cfceb945492819eaec8ce6a52051dec1d5621607b116fcde87b2565
   languageName: node
   linkType: hard
 
-"@storybook/cli@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/cli@npm:7.6.20"
+"@storybook/cli@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/cli@npm:7.6.21"
   dependencies:
     "@babel/core": "npm:^7.23.2"
     "@babel/preset-env": "npm:^7.23.2"
     "@babel/types": "npm:^7.23.0"
     "@ndelangen/get-tarball": "npm:^3.0.7"
-    "@storybook/codemod": "npm:7.6.20"
-    "@storybook/core-common": "npm:7.6.20"
-    "@storybook/core-events": "npm:7.6.20"
-    "@storybook/core-server": "npm:7.6.20"
-    "@storybook/csf-tools": "npm:7.6.20"
-    "@storybook/node-logger": "npm:7.6.20"
-    "@storybook/telemetry": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/codemod": "npm:7.6.21"
+    "@storybook/core-common": "npm:7.6.21"
+    "@storybook/core-events": "npm:7.6.21"
+    "@storybook/core-server": "npm:7.6.21"
+    "@storybook/csf-tools": "npm:7.6.21"
+    "@storybook/node-logger": "npm:7.6.21"
+    "@storybook/telemetry": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     "@types/semver": "npm:^7.3.4"
     "@yarnpkg/fslib": "npm:2.10.3"
     "@yarnpkg/libzip": "npm:2.3.0"
@@ -13401,89 +13401,89 @@ __metadata:
   bin:
     getstorybook: ./bin/index.js
     sb: ./bin/index.js
-  checksum: 10/0de9d7e77e1f0d97781b5acde906fe99c62caf182a9fcd1bbb7c852745208e74a8295c3cbbfcec41337a0d3ab7f97a43fdb3a6139f36ebabbe9b80b3c0fc2ca9
+  checksum: 10/4ba3fe2ea5d9d4f04ed3bdb3473ff280dcd7d69463c3723d7169523280a01e918a388753e4123d60890d1d5d24dd9c47a50ef43f8537275d956895661f787fdd
   languageName: node
   linkType: hard
 
-"@storybook/client-api@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/client-api@npm:7.6.20"
+"@storybook/client-api@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/client-api@npm:7.6.21"
   dependencies:
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/preview-api": "npm:7.6.20"
-  checksum: 10/094ebacca2c01a43659bbb22a88a415c196ad38c3cf1e752b544cd415566f3a5c71f528bb165cfcce80e7897b4c4e5ea6ae7d58a050207f5d1187822c17d8c91
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/preview-api": "npm:7.6.21"
+  checksum: 10/7c1018ef1dfb49e6b1f3d704dbf8bd9b5f5afcf5d6aaf1e2b3856425edce74ed706971eaaa15932668e67f682509331613e1a31073dbf6577221c4ff9f9ba0a3
   languageName: node
   linkType: hard
 
-"@storybook/client-logger@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/client-logger@npm:7.6.20"
+"@storybook/client-logger@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/client-logger@npm:7.6.21"
   dependencies:
     "@storybook/global": "npm:^5.0.0"
-  checksum: 10/0062c440c825ab460667d799b00d3ff87dcf4dabce05733c11ffbb1ea70e0a2e77fdc313ce9bdeccc4ac816101abe17572b96cc20c975874812f875828653704
+  checksum: 10/c72181c3a835aa71f82c673813d086d598eaf7708a57423744a7514736a307ffe58fee40a99a20296ccf99c0552fd6a13cdc375509fb5b1305810238464d8f7e
   languageName: node
   linkType: hard
 
-"@storybook/codemod@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/codemod@npm:7.6.20"
+"@storybook/codemod@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/codemod@npm:7.6.21"
   dependencies:
     "@babel/core": "npm:^7.23.2"
     "@babel/preset-env": "npm:^7.23.2"
     "@babel/types": "npm:^7.23.0"
     "@storybook/csf": "npm:^0.1.2"
-    "@storybook/csf-tools": "npm:7.6.20"
-    "@storybook/node-logger": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/csf-tools": "npm:7.6.21"
+    "@storybook/node-logger": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     "@types/cross-spawn": "npm:^6.0.2"
     cross-spawn: "npm:^7.0.3"
     globby: "npm:^11.0.2"
     jscodeshift: "npm:^0.15.1"
     lodash: "npm:^4.17.21"
     prettier: "npm:^2.8.0"
     recast: "npm:^0.23.1"
-  checksum: 10/ac4e2132be665e173bf7ce121341e847e6fed225e3fef4518a1a3d6f005d7677d116febe0d08f2ecb5f479823dcefa720ac4cf9b6b72ff9b557dbc7db7bd8b2f
+  checksum: 10/df123cafe5272891f4a3bbe050661d77cba3de444de1c1441911250f731217ffe8edd17be3489dcfdbfa1531e44293eaa884446a3f71694f04fbbe8f126dd6da
   languageName: node
   linkType: hard
 
-"@storybook/components@npm:7.6.20, @storybook/components@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/components@npm:7.6.20"
+"@storybook/components@npm:7.6.21, @storybook/components@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/components@npm:7.6.21"
   dependencies:
     "@radix-ui/react-select": "npm:^1.2.2"
     "@radix-ui/react-toolbar": "npm:^1.0.4"
-    "@storybook/client-logger": "npm:7.6.20"
+    "@storybook/client-logger": "npm:7.6.21"
     "@storybook/csf": "npm:^0.1.2"
     "@storybook/global": "npm:^5.0.0"
-    "@storybook/theming": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/theming": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     memoizerific: "npm:^1.11.3"
     use-resize-observer: "npm:^9.1.0"
     util-deprecate: "npm:^1.0.2"
   peerDependencies:
     react: ^16.8.0 || ^17.0.0 || ^18.0.0
     react-dom: ^16.8.0 || ^17.0.0 || ^18.0.0
-  checksum: 10/1b3e267ae73a4afad61aec99202e3d483dea079a02046bfa75ddb03726c5d59de4200f745c843b7c45dd8cea7159c85e2919ce83adff045f592fa04658d6d1e8
+  checksum: 10/8e4143412401fb72f03bdc7ff16022d134a84a7c3e1332849c9376b64c497a150dfeb60c9181cdb0cd1d7cbbec19bbb0fb314229c664c3990aa691439a0d8036
   languageName: node
   linkType: hard
 
-"@storybook/core-client@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/core-client@npm:7.6.20"
+"@storybook/core-client@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/core-client@npm:7.6.21"
   dependencies:
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/preview-api": "npm:7.6.20"
-  checksum: 10/e89fb4d9944715bed204371d8edf66b3d9038912b13e16962ea90e2d863331591b9dc10fa00a4218a4d770c56dd72bfc0b7d0a3ad3d7594cd3ebf218fa760a49
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/preview-api": "npm:7.6.21"
+  checksum: 10/54d3debd3ab8cd100e5733af5e966e203321a196392718231a6a4168a013f5f5dbfb938c13243a4da5db92e31e7c64d31da74abd651d2655d9c16d608aab1875
   languageName: node
   linkType: hard
 
-"@storybook/core-common@npm:7.6.20, @storybook/core-common@npm:^7.0.0-beta.0 || ^7.0.0-rc.0 || ^7.0.0":
-  version: 7.6.20
-  resolution: "@storybook/core-common@npm:7.6.20"
+"@storybook/core-common@npm:7.6.21, @storybook/core-common@npm:^7.0.0-beta.0 || ^7.0.0-rc.0 || ^7.0.0":
+  version: 7.6.21
+  resolution: "@storybook/core-common@npm:7.6.21"
   dependencies:
-    "@storybook/core-events": "npm:7.6.20"
-    "@storybook/node-logger": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/core-events": "npm:7.6.21"
+    "@storybook/node-logger": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     "@types/find-cache-dir": "npm:^3.2.1"
     "@types/node": "npm:^18.0.0"
     "@types/node-fetch": "npm:^2.6.4"
@@ -13504,38 +13504,38 @@ __metadata:
     pretty-hrtime: "npm:^1.0.3"
     resolve-from: "npm:^5.0.0"
     ts-dedent: "npm:^2.0.0"
-  checksum: 10/adc2c6dabd01904f10d2bce4f8d21fced023dfd3651661655844fa2e4f779e3774b1bf3328fd85e40091785bdb3a1cbb7bfca5b78c546493824322cd9ddae934
+  checksum: 10/dccb0047508e168ebcc965da4808a581b96a6689f24e85196d38f8c7c65b421fe8d1e7927c3709bab248ecf6d7356292bb722fb022db1ca761d2bbb8bd623cb4
   languageName: node
   linkType: hard
 
-"@storybook/core-events@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/core-events@npm:7.6.20"
+"@storybook/core-events@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/core-events@npm:7.6.21"
   dependencies:
     ts-dedent: "npm:^2.0.0"
-  checksum: 10/bd72649a262017f244aa6311352c1b38f2b38478c19b9aee4851bfdff5b2b11565dd768fe144f1304f9f130b533ffa4ab3fd2eea1361d202a76ff920cc377601
+  checksum: 10/942fdf60a7a5e08e80e07df7beee7855c311cdfea1a219b6f88f915706e5c78012b44da8ef1bd71e38c878ad1d10e9833fc36fb24b79f776312df19b5f560bad
   languageName: node
   linkType: hard
 
-"@storybook/core-server@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/core-server@npm:7.6.20"
+"@storybook/core-server@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/core-server@npm:7.6.21"
   dependencies:
     "@aw-web-design/x-default-browser": "npm:1.4.126"
     "@discoveryjs/json-ext": "npm:^0.5.3"
-    "@storybook/builder-manager": "npm:7.6.20"
-    "@storybook/channels": "npm:7.6.20"
-    "@storybook/core-common": "npm:7.6.20"
-    "@storybook/core-events": "npm:7.6.20"
+    "@storybook/builder-manager": "npm:7.6.21"
+    "@storybook/channels": "npm:7.6.21"
+    "@storybook/core-common": "npm:7.6.21"
+    "@storybook/core-events": "npm:7.6.21"
     "@storybook/csf": "npm:^0.1.2"
-    "@storybook/csf-tools": "npm:7.6.20"
+    "@storybook/csf-tools": "npm:7.6.21"
     "@storybook/docs-mdx": "npm:^0.1.0"
     "@storybook/global": "npm:^5.0.0"
-    "@storybook/manager": "npm:7.6.20"
-    "@storybook/node-logger": "npm:7.6.20"
-    "@storybook/preview-api": "npm:7.6.20"
-    "@storybook/telemetry": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/manager": "npm:7.6.21"
+    "@storybook/node-logger": "npm:7.6.21"
+    "@storybook/preview-api": "npm:7.6.21"
+    "@storybook/telemetry": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     "@types/detect-port": "npm:^1.3.0"
     "@types/node": "npm:^18.0.0"
     "@types/pretty-hrtime": "npm:^1.0.0"
@@ -13561,47 +13561,47 @@ __metadata:
     util-deprecate: "npm:^1.0.2"
     watchpack: "npm:^2.2.0"
     ws: "npm:^8.2.3"
-  checksum: 10/994dcdbd475650d396ad5f13113412779b23c910133e2fd45a2f7bd31c24a2bd351db977d6ae05b18dc6807edc7ac756286533145449e4e4f4d2bb99507586bb
+  checksum: 10/49041b7dfc9f654f5e4b71a3feb5ef7e8a1d9e21bfe578c30b36bd103dcf265492b95314f492712658b14a8ea2ae7326e281df34e8095616aeda13a98c461a43
   languageName: node
   linkType: hard
 
-"@storybook/core-webpack@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/core-webpack@npm:7.6.20"
+"@storybook/core-webpack@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/core-webpack@npm:7.6.21"
   dependencies:
-    "@storybook/core-common": "npm:7.6.20"
-    "@storybook/node-logger": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/core-common": "npm:7.6.21"
+    "@storybook/node-logger": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     "@types/node": "npm:^18.0.0"
     ts-dedent: "npm:^2.0.0"
-  checksum: 10/2277c5f996e2936955e19ba52600e286cf28eca7a24eba373329ca804e3e0d5da4047a15c01cdbb03abdf59690dbd96592c1f2c10d77af2463917555774ad9e0
+  checksum: 10/12ab7926dd1ca97950ed0f160eaeaff5ca5afdf01e0598bf4e3af4a721d52842655b5ed113b09379578aedd89f3478e4607a7f48c131c28a9f0e8b4c2be633ee
   languageName: node
   linkType: hard
 
-"@storybook/csf-plugin@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/csf-plugin@npm:7.6.20"
+"@storybook/csf-plugin@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/csf-plugin@npm:7.6.21"
   dependencies:
-    "@storybook/csf-tools": "npm:7.6.20"
+    "@storybook/csf-tools": "npm:7.6.21"
     unplugin: "npm:^1.3.1"
-  checksum: 10/0f40b4968e9abb0abf6657548fc6338755133b2c8bb788caf55b101b4558c9c55c428e357659723e06ab385a22fa96ba14059149c4473dd3d0190d6d21088a90
+  checksum: 10/da8cdd3ebf044d5405805d50946fe16f3c8fb76735c4a21bcf9713a7f112642f0544ec23cbb6f0cad2a86b006b8bbbb8c20f66ab2747dfc607e393a7c9a195fc
   languageName: node
   linkType: hard
 
-"@storybook/csf-tools@npm:7.6.20, @storybook/csf-tools@npm:^7.0.0-beta.0 || ^7.0.0-rc.0 || ^7.0.0":
-  version: 7.6.20
-  resolution: "@storybook/csf-tools@npm:7.6.20"
+"@storybook/csf-tools@npm:7.6.21, @storybook/csf-tools@npm:^7.0.0-beta.0 || ^7.0.0-rc.0 || ^7.0.0":
+  version: 7.6.21
+  resolution: "@storybook/csf-tools@npm:7.6.21"
   dependencies:
     "@babel/generator": "npm:^7.23.0"
     "@babel/parser": "npm:^7.23.0"
     "@babel/traverse": "npm:^7.23.2"
     "@babel/types": "npm:^7.23.0"
     "@storybook/csf": "npm:^0.1.2"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/types": "npm:7.6.21"
     fs-extra: "npm:^11.1.0"
     recast: "npm:^0.23.1"
     ts-dedent: "npm:^2.0.0"
-  checksum: 10/f0ca4a7e7309548bf647fbbc175bccb56fe4df210e3e52f96a5cc553bc06253c8fd7fcceb00ee7192e09fd073fd67fdaacab0ba81c56d440116114355b5f0935
+  checksum: 10/1b19f627cf84dc9806e2ebf57f71e40931911e30a1d7d253d309866415cc6075a6128da04aeca6de3c36d6a49fc860a752da5ae4910ae7a41168f2b5436572e6
   languageName: node
   linkType: hard
 
@@ -13630,18 +13630,18 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@storybook/docs-tools@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/docs-tools@npm:7.6.20"
+"@storybook/docs-tools@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/docs-tools@npm:7.6.21"
   dependencies:
-    "@storybook/core-common": "npm:7.6.20"
-    "@storybook/preview-api": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/core-common": "npm:7.6.21"
+    "@storybook/preview-api": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     "@types/doctrine": "npm:^0.0.3"
     assert: "npm:^2.1.0"
     doctrine: "npm:^3.0.0"
     lodash: "npm:^4.17.21"
-  checksum: 10/735a64bc90aaf51532104c6835e5fba7b30db33513b069404f3ed610ddfdd4c8689ea61630c1b6d04985a4faef8331d05ef95999983cdb244448229e5e3ef6bf
+  checksum: 10/5071f61bd1d9c2cc45cef7b0eee0069ab7df734b0e8847490dab1f502994b8282f707715aae3cbec04adeaf95eedaf80589a3c579eac2257ee0fd0580c1a1c8e
   languageName: node
   linkType: hard
 
@@ -13652,32 +13652,32 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@storybook/manager-api@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/manager-api@npm:7.6.20"
+"@storybook/manager-api@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/manager-api@npm:7.6.21"
   dependencies:
-    "@storybook/channels": "npm:7.6.20"
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/core-events": "npm:7.6.20"
+    "@storybook/channels": "npm:7.6.21"
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/core-events": "npm:7.6.21"
     "@storybook/csf": "npm:^0.1.2"
     "@storybook/global": "npm:^5.0.0"
-    "@storybook/router": "npm:7.6.20"
-    "@storybook/theming": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/router": "npm:7.6.21"
+    "@storybook/theming": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     dequal: "npm:^2.0.2"
     lodash: "npm:^4.17.21"
     memoizerific: "npm:^1.11.3"
     store2: "npm:^2.14.2"
     telejson: "npm:^7.2.0"
     ts-dedent: "npm:^2.0.0"
-  checksum: 10/ad66099e1bdcab11ac6542c65849b7dcf905207b2e6cc2bff8684450ce2b9838e1e913160803e4cd0d59c708400a25f0225d1b083853e737516e99eab6636315
+  checksum: 10/b43a820331438612f46f08a79babc803ab8e8720eb3f59f90e9cd5fa45310dd7d3270a466ed9f7c9f0d50b82755c864673bc08f7e7fe112312c3b2869e0bd39c
   languageName: node
   linkType: hard
 
-"@storybook/manager@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/manager@npm:7.6.20"
-  checksum: 10/542b5c765cf7704e157e6aea1bcf6b90e00cbb286251257b5e41bc35737f2df05215fecfdad89b3efa780341c1adf671eba71b7ee3164993bdf48bee3ad7c0a0
+"@storybook/manager@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/manager@npm:7.6.21"
+  checksum: 10/bbaf3ba9e031edcfb13cf662753024deb3f2720f35fa4a44a44caae7b6255f398a00a029f0b5ac9f475172dc79a0e4419a99feab002ea628e5509b1bacc2a157
   languageName: node
   linkType: hard
 
@@ -13688,31 +13688,31 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@storybook/node-logger@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/node-logger@npm:7.6.20"
-  checksum: 10/4e6cf2be559e91b111142cdd2ed7c742f2d231ea30c3df773de0e1daec9986c4db3724ddf3c6dcbc873784a49dc8c7a9e3780037d0690a95a0a0c2d6b7ce0968
+"@storybook/node-logger@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/node-logger@npm:7.6.21"
+  checksum: 10/127408607afe07f4a675cd5947206b9b2b199040d625aa24a9b6f8219e462cfafa4514d8c0dceec6d585c6d80aa24cc0da1231ca9474929faac75254b0239f9b
   languageName: node
   linkType: hard
 
-"@storybook/postinstall@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/postinstall@npm:7.6.20"
-  checksum: 10/bb743168ce64e90d95ded66742d76cf4818d41a29e84f6d88044f680f83e24fbce159555670754fe58a414193139373ea03c7699adbac3599e860eed092c11bc
+"@storybook/postinstall@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/postinstall@npm:7.6.21"
+  checksum: 10/86df9ca2de2a49b75ec774590e38880bc5e6631123b271d6459b0940f95bdabae64c20758b99b42400a0906feaad28b047a3b86081033b0dcbe1d5537bfa082a
   languageName: node
   linkType: hard
 
-"@storybook/preset-react-webpack@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/preset-react-webpack@npm:7.6.20"
+"@storybook/preset-react-webpack@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/preset-react-webpack@npm:7.6.21"
   dependencies:
     "@babel/preset-flow": "npm:^7.22.15"
     "@babel/preset-react": "npm:^7.22.15"
     "@pmmmwh/react-refresh-webpack-plugin": "npm:^0.5.11"
-    "@storybook/core-webpack": "npm:7.6.20"
-    "@storybook/docs-tools": "npm:7.6.20"
-    "@storybook/node-logger": "npm:7.6.20"
-    "@storybook/react": "npm:7.6.20"
+    "@storybook/core-webpack": "npm:7.6.21"
+    "@storybook/docs-tools": "npm:7.6.21"
+    "@storybook/node-logger": "npm:7.6.21"
+    "@storybook/react": "npm:7.6.21"
     "@storybook/react-docgen-typescript-plugin": "npm:1.0.6--canary.9.0c3f3b7.0"
     "@types/node": "npm:^18.0.0"
     "@types/semver": "npm:^7.3.4"
@@ -13732,20 +13732,20 @@ __metadata:
       optional: true
     typescript:
       optional: true
-  checksum: 10/bcce20358d85b5fb143a3bb184d4305ba96c4c54bed09b61b3a10e6748e4c3721069b7f7c89f9a1d62ba8234c215759a38d4d39f26e3e6b0c2b19a8ce23e13a1
+  checksum: 10/b6215eaefff5e59f93112a0f1a9553da5dc7c311208075735a7ae1cd9a62c7e469a77761ac85aa65b7988c53c8c9f7fccdce6e45c8a2bf7f681a4f6dd2ded360
   languageName: node
   linkType: hard
 
-"@storybook/preview-api@npm:7.6.20, @storybook/preview-api@npm:^7.0.0-beta.0 || ^7.0.0-rc.0 || ^7.0.0":
-  version: 7.6.20
-  resolution: "@storybook/preview-api@npm:7.6.20"
+"@storybook/preview-api@npm:7.6.21, @storybook/preview-api@npm:^7.0.0-beta.0 || ^7.0.0-rc.0 || ^7.0.0":
+  version: 7.6.21
+  resolution: "@storybook/preview-api@npm:7.6.21"
   dependencies:
-    "@storybook/channels": "npm:7.6.20"
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/core-events": "npm:7.6.20"
+    "@storybook/channels": "npm:7.6.21"
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/core-events": "npm:7.6.21"
     "@storybook/csf": "npm:^0.1.2"
     "@storybook/global": "npm:^5.0.0"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/types": "npm:7.6.21"
     "@types/qs": "npm:^6.9.5"
     dequal: "npm:^2.0.2"
     lodash: "npm:^4.17.21"
@@ -13754,14 +13754,14 @@ __metadata:
     synchronous-promise: "npm:^2.0.15"
     ts-dedent: "npm:^2.0.0"
     util-deprecate: "npm:^1.0.2"
-  checksum: 10/1facc19c6f3723d509114e3023dca1d19fd28f199673c81b77a2f31dea6d13c31455ce3b0eb57841e77b438479df9a6b73f2d5d0d4636bb123a3637c81910b49
+  checksum: 10/06ec3893ef91b895a3d89c466cd6a8075bdc2d6ed70f1667823aa89294bd1528b2f2a959af9cdf55b33eeb176d522242a70119e4ef924cfbf7c9056a0b3a8b60
   languageName: node
   linkType: hard
 
-"@storybook/preview@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/preview@npm:7.6.20"
-  checksum: 10/1d1e4c7dc47898467f8ce9caa5026e902e420dac23a51782f3e65ecb50639d0cc1b0b32b7d28ad82b9c7b5e0ffcb528911948fbd952ac45aaec0ccace9aecd71
+"@storybook/preview@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/preview@npm:7.6.21"
+  checksum: 10/ea08d8f9813082d17b3401d6fbe24bf4abe0468be644d51a0e3bec379f63d23fa41eba6de955a9d13d805ae697109088c89965189863cc0472d897e6e05140ec
   languageName: node
   linkType: hard
 
@@ -13783,23 +13783,23 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@storybook/react-dom-shim@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/react-dom-shim@npm:7.6.20"
+"@storybook/react-dom-shim@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/react-dom-shim@npm:7.6.21"
   peerDependencies:
     react: ^16.8.0 || ^17.0.0 || ^18.0.0
     react-dom: ^16.8.0 || ^17.0.0 || ^18.0.0
-  checksum: 10/8639816eda50e2ca507a9cb78d5a67b9aaabd26ca03177fb93c5de9d233f0bb3e708524fc8ce14df0c7d3d65347ec581df922c28ceee7df265c2e04bf5b72784
+  checksum: 10/6481be6fe7df44575e679313ff461752a0bd76c6fac71dac9f84d875eb192247e30462e9eadbec7fb1f651e5edebacd4833763d29fda18a3d2670ea0b18b404a
   languageName: node
   linkType: hard
 
-"@storybook/react-webpack5@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/react-webpack5@npm:7.6.20"
+"@storybook/react-webpack5@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/react-webpack5@npm:7.6.21"
   dependencies:
-    "@storybook/builder-webpack5": "npm:7.6.20"
-    "@storybook/preset-react-webpack": "npm:7.6.20"
-    "@storybook/react": "npm:7.6.20"
+    "@storybook/builder-webpack5": "npm:7.6.21"
+    "@storybook/preset-react-webpack": "npm:7.6.21"
+    "@storybook/react": "npm:7.6.21"
     "@types/node": "npm:^18.0.0"
   peerDependencies:
     "@babel/core": ^7.22.0
@@ -13811,21 +13811,21 @@ __metadata:
       optional: true
     typescript:
       optional: true
-  checksum: 10/a6213abdbdc652d7acc045d7aa716f696090f0813b8234acbc2c6fa71282556e0207ebf36aa3d74f6ab1980a0a43bc7b4b431fd9377912b8a253e1ab0ee1c124
+  checksum: 10/4975ec00a9d9090b421c521029e4c7e45f1dbf6532e88e7b4dcf3b7b9d805d3932327bdea353bb2e0badf67f141a826fc2079e8eca94fa1db3d2df09649904dc
   languageName: node
   linkType: hard
 
-"@storybook/react@npm:7.6.20, @storybook/react@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/react@npm:7.6.20"
+"@storybook/react@npm:7.6.21, @storybook/react@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/react@npm:7.6.21"
   dependencies:
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/core-client": "npm:7.6.20"
-    "@storybook/docs-tools": "npm:7.6.20"
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/core-client": "npm:7.6.21"
+    "@storybook/docs-tools": "npm:7.6.21"
     "@storybook/global": "npm:^5.0.0"
-    "@storybook/preview-api": "npm:7.6.20"
-    "@storybook/react-dom-shim": "npm:7.6.20"
-    "@storybook/types": "npm:7.6.20"
+    "@storybook/preview-api": "npm:7.6.21"
+    "@storybook/react-dom-shim": "npm:7.6.21"
+    "@storybook/types": "npm:7.6.21"
     "@types/escodegen": "npm:^0.0.6"
     "@types/estree": "npm:^0.0.51"
     "@types/node": "npm:^18.0.0"
@@ -13847,18 +13847,18 @@ __metadata:
   peerDependenciesMeta:
     typescript:
       optional: true
-  checksum: 10/2a0602c42b91a52fd6247b94933680caa498469104311793613a473f2cb395aa467e837d1094fcf0b4becb2b83b34026bef4a7a1c4e238546c800ab8167f2b06
+  checksum: 10/570c140ec6cc8f9b6d337b56a519ee921a585f1b725cd57b1f0e612ca189677ff59c71658d381a446ebe176cbf48f0203c2dcd0f372625b3057962b158f0697a
   languageName: node
   linkType: hard
 
-"@storybook/router@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/router@npm:7.6.20"
+"@storybook/router@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/router@npm:7.6.21"
   dependencies:
-    "@storybook/client-logger": "npm:7.6.20"
+    "@storybook/client-logger": "npm:7.6.21"
     memoizerific: "npm:^1.11.3"
     qs: "npm:^6.10.0"
-  checksum: 10/dd7a7ef64efc4d7d133be1f17667b2d8d8a0b6ee8738ce971d783fb4b0c9213d52cacc08513287e36683b3ea93f94e91b5211a458dad466006213cb1bfa12f4a
+  checksum: 10/99aaa61caff0e3296de3cebf543ba359404db55f87cacc130969d732e8a6a496fc269d5bcee50188eaccce258de081b9d083300e395736edce3fb8bfad3c9f4b
   languageName: node
   linkType: hard
 
@@ -13878,19 +13878,19 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@storybook/telemetry@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/telemetry@npm:7.6.20"
+"@storybook/telemetry@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/telemetry@npm:7.6.21"
   dependencies:
-    "@storybook/client-logger": "npm:7.6.20"
-    "@storybook/core-common": "npm:7.6.20"
-    "@storybook/csf-tools": "npm:7.6.20"
+    "@storybook/client-logger": "npm:7.6.21"
+    "@storybook/core-common": "npm:7.6.21"
+    "@storybook/csf-tools": "npm:7.6.21"
     chalk: "npm:^4.1.0"
     detect-package-manager: "npm:^2.0.1"
     fetch-retry: "npm:^5.0.2"
     fs-extra: "npm:^11.1.0"
     read-pkg-up: "npm:^7.0.1"
-  checksum: 10/ce679a0b1bf975e7de6ca77f40942ade9f549da156d40c019e9b3bbbdf87cdb5a4ffdea52b80315f6af5354e3a51e7b4241b8d514c78d7403c99648318bc3246
+  checksum: 10/0909c2609d8ed72d95132d30c0718bba61d28cc300ef9f315592168dbc1b5a95668a8a7f8adf670ba47d67d0ea312ab2042556b6e3a4c03bb21df5ca8e78654f
   languageName: node
   linkType: hard
 
@@ -13931,30 +13931,30 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@storybook/theming@npm:7.6.20, @storybook/theming@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/theming@npm:7.6.20"
+"@storybook/theming@npm:7.6.21, @storybook/theming@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/theming@npm:7.6.21"
   dependencies:
     "@emotion/use-insertion-effect-with-fallbacks": "npm:^1.0.0"
-    "@storybook/client-logger": "npm:7.6.20"
+    "@storybook/client-logger": "npm:7.6.21"
     "@storybook/global": "npm:^5.0.0"
     memoizerific: "npm:^1.11.3"
   peerDependencies:
     react: ^16.8.0 || ^17.0.0 || ^18.0.0
     react-dom: ^16.8.0 || ^17.0.0 || ^18.0.0
-  checksum: 10/c26ba05d8fa1ba6c9d62b1d690dc55ba56874c493a7dfef5e85df89fc1da2ce8be09d7426071e43dbb3bf16ca4bc579a94f8f1a1ab14cfd29465a6a6eca5b158
+  checksum: 10/d9ef2f0b4d945da49d1433a6652221c53addfa927f1110468960dfa4283b3756de739b05fdbc6ae482a328394827e8adae9242db569caa3e26b136cf3358014c
   languageName: node
   linkType: hard
 
-"@storybook/types@npm:7.6.20":
-  version: 7.6.20
-  resolution: "@storybook/types@npm:7.6.20"
+"@storybook/types@npm:7.6.21":
+  version: 7.6.21
+  resolution: "@storybook/types@npm:7.6.21"
   dependencies:
-    "@storybook/channels": "npm:7.6.20"
+    "@storybook/channels": "npm:7.6.21"
     "@types/babel__core": "npm:^7.0.0"
     "@types/express": "npm:^4.7.0"
     file-system-cache: "npm:2.3.0"
-  checksum: 10/8da9513f1f34f606b114026af5fad5a7658ce5e2fa7af3363d9f3d481e5e22ed9ae6343f28aa9d14208bff07f489cb7f5ae3adcad5a603f8181e952b2ee29f3f
+  checksum: 10/207ddd1aaf3b33beb488952a916dc37998290d60eb300f6ae762717e6071b34e9b10a8351dbedac6e7311b0b5619dfbb808505314a3c67864b8700340ac2e66f
   languageName: node
   linkType: hard
 
@@ -32955,19 +32955,19 @@ __metadata:
     "@slack/types": "npm:^2.14.0"
     "@slack/webhook": "npm:^7.0.5"
     "@solana/addresses": "npm:2.0.0-rc.4"
-    "@storybook/addon-a11y": "npm:^7.6.20"
-    "@storybook/addon-actions": "npm:^7.6.20"
-    "@storybook/addon-docs": "npm:^7.6.20"
-    "@storybook/addon-essentials": "npm:^7.6.20"
-    "@storybook/addons": "npm:^7.6.20"
-    "@storybook/api": "npm:^7.6.20"
-    "@storybook/client-api": "npm:^7.6.20"
-    "@storybook/components": "npm:^7.6.20"
-    "@storybook/react": "npm:^7.6.20"
-    "@storybook/react-webpack5": "npm:^7.6.20"
+    "@storybook/addon-a11y": "npm:^7.6.21"
+    "@storybook/addon-actions": "npm:^7.6.21"
+    "@storybook/addon-docs": "npm:^7.6.21"
+    "@storybook/addon-essentials": "npm:^7.6.21"
+    "@storybook/addons": "npm:^7.6.21"
+    "@storybook/api": "npm:^7.6.21"
+    "@storybook/client-api": "npm:^7.6.21"
+    "@storybook/components": "npm:^7.6.21"
+    "@storybook/react": "npm:^7.6.21"
+    "@storybook/react-webpack5": "npm:^7.6.21"
     "@storybook/storybook-deployer": "npm:^2.8.16"
     "@storybook/test-runner": "npm:^0.14.1"
-    "@storybook/theming": "npm:^7.6.20"
+    "@storybook/theming": "npm:^7.6.21"
     "@swc/core": "npm:^1.13.2"
     "@swc/helpers": "npm:^0.5.17"
     "@tanstack/react-virtual": "npm:^3.10.8"
@@ -33215,7 +33215,7 @@ __metadata:
     source-map: "npm:^0.7.4"
     source-map-explorer: "npm:^2.4.2"
     sprintf-js: "npm:^1.1.3"
-    storybook: "npm:^7.6.20"
+    storybook: "npm:^7.6.21"
     stream-browserify: "npm:^3.0.0"
     stream-http: "npm:^3.2.0"
     string.prototype.matchall: "npm:^4.0.2"
@@ -40760,15 +40760,15 @@ __metadata:
   languageName: node
   linkType: hard
 
-"storybook@npm:^7.6.20":
-  version: 7.6.20
-  resolution: "storybook@npm:7.6.20"
+"storybook@npm:^7.6.21":
+  version: 7.6.21
+  resolution: "storybook@npm:7.6.21"
   dependencies:
-    "@storybook/cli": "npm:7.6.20"
+    "@storybook/cli": "npm:7.6.21"
   bin:
     sb: ./index.js
     storybook: ./index.js
-  checksum: 10/7442d0bf404fafdfa6921d388b7af78e835bd4278ec7cc0c6565d3723cb1cd7d24621a97186abd553f1345ddf78628e517656af64bcb4a3d9e9c6253b01461e8
+  checksum: 10/a58bfff2a0c18a976d1095bb076f9c1228fe85f468398006402c43b70a47b73f906faab46700a4a4539f51a64d475253fc801510b5cf1edccdcfc998fbb46f1f
   languageName: node
   linkType: hard
 
```
