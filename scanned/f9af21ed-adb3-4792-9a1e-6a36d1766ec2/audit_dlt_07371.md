# [?] chore(security): Set yarn resolution for `qs` to patch vulnerability (#39015)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-01-05
Source: https://github.com/MetaMask/metamask-extension/commit/2a887cd3d272de7a9c47ffeccecc7e1825b01c60
Type: security-commit

## Details
chore(security): Set yarn resolution for `qs` to patch vulnerability (#39015)

<!--
Please submit this PR as a draft initially.
Do not mark it as "Ready for review" until the template has been
completely filled out, and PR status checks have passed at least once.
-->

## **Description**

<!--
Write a short description of the changes included in this pull request,
also include relevant motivation and context. Have in mind the following
questions:
1. What is the reason for the change?
2. What is the improvement/solution?
-->

Resolves:
```
Run yarn audit
└─ qs
   ├─ ID: 1111755
   ├─ Issue: qs's arrayLimit bypass in its bracket notation allows DoS via memory exhaustion
   ├─ URL: https://github.com/advisories/GHSA-6rw7-vpxm-498p
   ├─ Severity: high
   ├─ Vulnerable Versions: <6.14.1
   │ 
   ├─ Tree Versions
   │  └─ 6.13.0
   │ 
   └─ Dependents
      └─ express@npm:4.21.2
```
> Example failing `yarn audit` run:
https://github.com/MetaMask/metamask-extension/actions/runs/20714938664/job/59463900086?pr=38852

[![Open in GitHub
Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MetaMask/metamask-extension/pull/39015?quickstart=1)

## **Changelog**

<!--
If this PR is not End-User-Facing and should not show up in the
CHANGELOG, you can choose to either:
1. Write `CHANGELOG entry: null`
2. Label with `no-changelog`

If this PR is End-User-Facing, please write a short User-Facing
description in the past tense like:
`CHANGELOG entry: Added a new tab for users to see their NFTs`
`CHANGELOG entry: Fixed a bug that was causing some NFTs to flicker`

(This helps the Release Engineer do their job more quickly and
accurately)
-->

CHANGELOG entry: null

## **Related issues**

Fixes:

## **Manual testing steps**

1. Go to this page...
2.
3.

## **Screenshots/Recordings**

<!-- If applicable, add screenshots and/or recordings to visualize the
before and after of your change. -->

### **Before**

<!-- [screenshots/recordings] -->

### **After**

<!-- [screenshots/recordings] -->

## **Pre-merge author checklist**

- [ ] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [ ] I've completed the PR template to the best of my ability
- [ ] I’ve included tests if applicable
- [ ] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [ ] I’ve applied the right labels on the PR (see [labeling
guidelines](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/LABELING_GUIDELINES.md)).
Not required for external contributors.

## **Pre-merge reviewer checklist**

- [ ] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [ ] I confirm that this PR addresses all acceptance criteria described
in the ticket it closes and includes the necessary testing evidence such
as recordings and or screenshots.

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Addresses qs vulnerability by standardizing on 6.14.1 and updating
related security policy mappings.
> 
> - Add Yarn resolution `"qs@6.13.0": "^6.14.1"` in `package.json`
> - Update `yarn.lock` to dedupe `qs` to `6.14.1` and adjust
`side-channel` range
> - Update LavaMoat policy files (`lavamoat/*/policy.json`) to replace
`browserify>url>qs` with `mockttp>express>qs`, including within
`browserify>url` package lists
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
7865dee1bfc84c2c4a8801ac85f25a773fdec36b. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

---------

Co-authored-by: MetaMask Bot <metamaskbot@users.noreply.github.com>

## Patch
### lavamoat/browserify/beta/policy.json
```diff
@@ -4590,7 +4590,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5513,7 +5513,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/browserify/experimental/policy.json
```diff
@@ -4590,7 +4590,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5513,7 +5513,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/browserify/flask/policy.json
```diff
@@ -4590,7 +4590,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5513,7 +5513,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/browserify/main/policy.json
```diff
@@ -4590,7 +4590,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5513,7 +5513,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/build-system/policy.json
```diff
@@ -5713,7 +5713,7 @@
         "gulp>vinyl-fs>pumpify>pump": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -8220,7 +8220,7 @@
         "gulp-livereload>tiny-lr>debug": true,
         "gulp-livereload>tiny-lr>faye-websocket": true,
         "react>object-assign": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "gulp>vinyl-fs>glob-stream>to-absolute-glob": {
```

### lavamoat/webpack/mv2/policy.json
```diff
@@ -4873,7 +4873,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5951,7 +5951,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/webpack/mv3/policy.json
```diff
@@ -3294,7 +3294,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -4245,7 +4245,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### package.json
```diff
@@ -255,7 +255,8 @@
     "@metamask/assets-controllers@npm:^91.0.0": "patch:@metamask/assets-controllers@npm%3A93.1.0#~/.yarn/patches/@metamask-assets-controllers-npm-93.1.0-0f2b5956ff.patch",
     "which@npm:^1.2.12": "^4.0.0",
     "which@npm:^1.2.14": "^4.0.0",
-    "which@npm:^1.3.1": "^4.0.0"
+    "which@npm:^1.3.1": "^4.0.0",
+    "qs@npm:6.13.0": "^6.14.1"
   },
   "dependencies": {
     "@babel/runtime": "patch:@babel/runtime@npm%3A7.25.9#~/.yarn/patches/@babel-runtime-npm-7.25.9-fe8c62510a.patch",
```

### yarn.lock
```diff
@@ -36983,21 +36983,12 @@ __metadata:
   languageName: node
   linkType: hard
 
-"qs@npm:6.13.0":
-  version: 6.13.0
-  resolution: "qs@npm:6.13.0"
-  dependencies:
-    side-channel: "npm:^1.0.6"
-  checksum: 10/f548b376e685553d12e461409f0d6e5c59ec7c7d76f308e2a888fd9db3e0c5e89902bedd0754db3a9038eda5f27da2331a6f019c8517dc5e0a16b3c9a6e9cef8
-  languageName: node
-  linkType: hard
-
-"qs@npm:^6.10.0, qs@npm:^6.12.3, qs@npm:^6.4.0":
-  version: 6.14.0
-  resolution: "qs@npm:6.14.0"
+"qs@npm:^6.10.0, qs@npm:^6.12.3, qs@npm:^6.14.1, qs@npm:^6.4.0":
+  version: 6.14.1
+  resolution: "qs@npm:6.14.1"
   dependencies:
     side-channel: "npm:^1.1.0"
-  checksum: 10/a60e49bbd51c935a8a4759e7505677b122e23bf392d6535b8fc31c1e447acba2c901235ecb192764013cd2781723dc1f61978b5fdd93cc31d7043d31cdc01974
+  checksum: 10/34b5ab00a910df432d55180ef39c1d1375e550f098b5ec153b41787f1a6a6d7e5f9495593c3b112b77dbc6709d0ae18e55b82847a4c2bbbb0de1e8ccbb1794c5
   languageName: node
   linkType: hard
 
@@ -40100,7 +40091,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"side-channel@npm:^1.0.4, side-channel@npm:^1.0.6, side-channel@npm:^1.1.0":
+"side-channel@npm:^1.0.4, side-channel@npm:^1.1.0":
   version: 1.1.0
   resolution: "side-channel@npm:1.1.0"
   dependencies:
```
