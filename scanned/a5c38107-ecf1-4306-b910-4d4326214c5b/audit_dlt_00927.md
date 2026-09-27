# [?] release(runway): cherry-pick chore: bump `dompurify` to `3.4.13` to clear `GHSA-55q2-fjhq-7xh7` (#45377)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-08-10
Source: https://github.com/MetaMask/metamask-extension/commit/a70b6f95abc9bd9cf01166410c80a3899634778f
Type: security-commit

## Details
release(runway): cherry-pick chore: bump `dompurify` to `3.4.13` to clear `GHSA-55q2-fjhq-7xh7` (#45377)

- chore: bump `dompurify` to `3.4.13` to clear `GHSA-55q2-fjhq-7xh7`
cp-13.43.0 (#45364)

## **Description**

`dompurify` is a direct production dependency.
[GHSA-55q2-fjhq-7xh7](https://github.com/advisories/GHSA-55q2-fjhq-7xh7)
covers `<= 3.4.12` — during `IN_PLACE` sanitization a hook that removes
an element leaves that element's detached descendants executable,
because `_sanitizeElements()` returns early without calling
`_neutralizeSubtree()`.

**This is not a plain version bump.** `dompurify` was declared *as a
patch spec* in both `dependencies` and `resolutions`, each hard-pinning
the exact version 3.4.12, so `yarn up dompurify` cannot move it. Three
things change together:

- the dependency spec → `patch:dompurify@npm%3A3.4.13#...`
- the matching `resolutions` entry
- the patch itself, rebased 3.4.12 → 3.4.13 via `yarn patch` / `yarn
patch-commit`

**The carried-forward patch is unrelated to this advisory** — it
rewrites `'<!-->'` and `'<!---->'` as concatenations so the literals do
not trip LavaMoat's `SES_HTML_COMMENT_REJECTED`. Same two edits, only
line offsets moved:

```diff
-      dirty = '<!-->';
+      // Modifying to avoid lavamoat SES_HTML_COMMENT_REJECTED
+      dirty = '<!' + '--' + '>';
-      body = _initDocument('<!---->');
+      // Modifying to avoid lavamoat SES_HTML_COMMENT_REJECTED
+      body = _initDocument('<!' + '--' + '--' + '>');
```

### Patch scope: carried forward unchanged

The 3.4.12 patch covered three bundles; this covers the same three — 3
files, 6 hunks. `dist/purify.js` is the UMD build, so it takes the same
two edits one indent level deeper.

Verified rather than asserted — both the `+`/`-` content and the file
set diff clean against the 3.4.12 patch:

```
diff <(grep -E '^[+-]' old.patch | grep -vE '^(\+\+\+|---)' | sort) \
     <(grep -E '^[+-]' new.patch | grep -vE '^(\+\+\+|---)' | sort)   # no output
```

## **Changelog**

CHANGELOG entry: null

## **Related issues**

Fixes: #45325

Reachability triage for this advisory — why the vulnerable path is not
reachable as we use DOMPurify, and why an upgrade was still the cheaper
disposition than a suppression with a guarded invariant:

https://github.com/MetaMask/metamask-extension/issues/45325#issuecomment-5241322193

## **Manual testing steps**

Verification is against the **installed artifact**, not the manifest — a
patch that silently failed to apply would still leave `package.json`
looking correct.

1. `yarn install`
2. `cat node_modules/dompurify/package.json | grep version` → `3.4.13`
3. `grep -c "'<!' + '--'"
node_modules/dompurify/dist/purify.{cjs.js,es.mjs}` → `2` each (patch
applied)
4. `grep -c "dirty = '<!-->'"
node_modules/dompurify/dist/purify.{cjs.js,es.mjs}` → `0` each (no
unpatched literals)
5. `grep -c "_neutralizeSubtree(currentNode)"
node_modules/dompurify/dist/purify.cjs.js` → `2` (upstream fix present
on both hook-detach paths)
6. `yarn npm audit --recursive --environment production`
7. `yarn jest
ui/pages/notifications/notification-components/feature-announcement`

### Results on this branch

| check | result |
|---|---|
| installed version | **3.4.13** |
| SES patch applied | 2 occurrences in each of all three bundles |
| patch scope | 3 files / 6 hunks — identical file set and `+`/`-`
content to the 3.4.12 patch |
| unpatched literals remaining | **0** in both files |
| upstream fix present | `_neutralizeSubtree(currentNode)` guards
**both** hook-detach returns |
| production audit | dompurify **not flagged** |
| consumer tests | **11/11 passing** |
| diff scope | `package.json` 4 lines, `yarn.lock` 18 lines, patch
renamed 3.4.12 → 3.4.13 |

## **Screenshots/Recordings**

N/A — no user-visible change.

## **Pre-merge author checklist**

- [x] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding

Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [x] I've completed the PR template to the best of my ability
- [ ] I’ve included tests if applicable — N/A, dependency bump; existing
consumer suite exercised
- [ ] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable — N/A
- [x] I’ve applied the right labels on the PR (see [labeling

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
> **Low Risk**
> Dependency-only security upgrade with the same behavioral patch as
before; no application code changes, though dompurify is on the HTML
sanitization path.
> 
> **Overview**
> **Upgrades `dompurify` from 3.4.12 to 3.4.13** to address
**GHSA-55q2-fjhq-7xh7** (hook-driven element removal could leave
detached descendants unsanitized in `IN_PLACE` mode). Because the
dependency is pinned as a Yarn **patch** spec in both `dependencies` and
`resolutions`, the change updates those entries and `yarn.lock` to
`patch:dompurify@npm%3A3.4.13#...` rather than a simple version bump.
> 
> The existing **LavaMoat** workaround is **rebased unchanged** onto
3.4.13: HTML comment placeholders (`'<!-->'`, `'<!---->'`) are built via
string concatenation in the three dist bundles so they do not trigger
`SES_HTML_COMMENT_REJECTED`.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
f49a90ac5a54f6e76f7d0d82a899f6518c572206. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->
[0967a06](https://github.com/MetaMask/metamask-extension/commit/0967a06b6b3d590298c784283af51b38ede92e76)

---------

Co-authored-by: Jongsun Suh <jongsun.suh@icloud.com>
Co-authored-by: MetaMask Bot <metamaskbot@users.noreply.github.com>

### .yarn/patches/dompurify-npm-3.4.13-71386e31f7.patch
```diff
@@ -1,8 +1,8 @@
 diff --git a/dist/purify.cjs.js b/dist/purify.cjs.js
-index 91b993d668dd9780a88ea26ba6bf60eb17ef07bb..603ec9c2233ab857afee32fbf4af4c35895c154d 100644
+index 1b3a886b5444b7732e3f9ca4dbbc24d098b681df..c804479deb3d160cb44f729ab3231980af793f4d 100644
 --- a/dist/purify.cjs.js
 +++ b/dist/purify.cjs.js
-@@ -2128,7 +2128,8 @@ function createDOMPurify() {
+@@ -2188,7 +2188,8 @@ function createDOMPurify() {
        the user has requested a DOM object rather than a string */
      IS_EMPTY_INPUT = !dirty;
      if (IS_EMPTY_INPUT) {
@@ -12,7 +12,7 @@ index 91b993d668dd9780a88ea26ba6bf60eb17ef07bb..603ec9c2233ab857afee32fbf4af4c35
      }
      /* Stringify, in case dirty is an object */
      if (typeof dirty !== 'string' && !_isNode(dirty)) {
-@@ -2228,7 +2229,8 @@ function createDOMPurify() {
+@@ -2288,7 +2289,8 @@ function createDOMPurify() {
      } else if (_isNode(dirty)) {
        /* If dirty is a DOM element, append to an empty document to avoid
           elements being stripped by the parser */
@@ -23,10 +23,10 @@ index 91b993d668dd9780a88ea26ba6bf60eb17ef07bb..603ec9c2233ab857afee32fbf4af4c35
        if (importedNode.nodeType === NODE_TYPE.element && importedNode.nodeName === 'BODY') {
          /* Node is already a body, use as is */
 diff --git a/dist/purify.es.mjs b/dist/purify.es.mjs
-index 3c361d7afae9348d7e12d046a598a4dabb4ba423..489289ac87b83c35f3c7981d342a71da74f5126c 100644
+index 1933f9df555ff132e549b3489ee8bb01e556a3a7..8bba53ce5d279561f41f4d9287ff9ebbad6d7d4d 100644
 --- a/dist/purify.es.mjs
 +++ b/dist/purify.es.mjs
-@@ -2126,7 +2126,8 @@ function createDOMPurify() {
+@@ -2186,7 +2186,8 @@ function createDOMPurify() {
        the user has requested a DOM object rather than a string */
      IS_EMPTY_INPUT = !dirty;
      if (IS_EMPTY_INPUT) {
@@ -36,7 +36,7 @@ index 3c361d7afae9348d7e12d046a598a4dabb4ba423..489289ac87b83c35f3c7981d342a71da
      }
      /* Stringify, in case dirty is an object */
      if (typeof dirty !== 'string' && !_isNode(dirty)) {
-@@ -2226,7 +2227,8 @@ function createDOMPurify() {
+@@ -2286,7 +2287,8 @@ function createDOMPurify() {
      } else if (_isNode(dirty)) {
        /* If dirty is a DOM element, append to an empty document to avoid
           elements being stripped by the parser */
@@ -47,10 +47,10 @@ index 3c361d7afae9348d7e12d046a598a4dabb4ba423..489289ac87b83c35f3c7981d342a71da
        if (importedNode.nodeType === NODE_TYPE.element && importedNode.nodeName === 'BODY') {
          /* Node is already a body, use as is */
 diff --git a/dist/purify.js b/dist/purify.js
-index 0ec2e6e0158b8b535d7ab50d66104f56de748e22..e9f021c6861d2883fbb38d4953be674a8e136f6a 100644
+index d013573e7a72a84887652b7b2c5f2ee0582d94a1..bcdd150c5b3d9ea933e824bc8f4c508586d3a49a 100644
 --- a/dist/purify.js
 +++ b/dist/purify.js
-@@ -2132,7 +2132,8 @@
+@@ -2192,7 +2192,8 @@
          the user has requested a DOM object rather than a string */
        IS_EMPTY_INPUT = !dirty;
        if (IS_EMPTY_INPUT) {
@@ -60,7 +60,7 @@ index 0ec2e6e0158b8b535d7ab50d66104f56de748e22..e9f021c6861d2883fbb38d4953be674a
        }
        /* Stringify, in case dirty is an object */
        if (typeof dirty !== 'string' && !_isNode(dirty)) {
-@@ -2232,7 +2233,8 @@
+@@ -2292,7 +2293,8 @@
        } else if (_isNode(dirty)) {
          /* If dirty is a DOM element, append to an empty document to avoid
             elements being stripped by the parser */
```

### attribution.txt
```diff
@@ -6591,7 +6591,7 @@ SOFTWARE.
 ******************************
 
 dompurify
-3.4.12 <https://github.com/cure53/DOMPurify>
+3.4.13 <https://github.com/cure53/DOMPurify>
 
                                  Apache License
                            Version 2.0, January 2004
```

### package.json
```diff
@@ -267,7 +267,7 @@
     "@trezor/connect-web": "~9.6.0",
     "nanoid@npm:^5.1.5": "^3.3.8",
     "lodash": "patch:lodash@npm%3A4.18.1#~/.yarn/patches/lodash-npm-4.18.1-a64c3070ac.patch",
-    "dompurify": "patch:dompurify@npm%3A3.4.12#~/.yarn/patches/dompurify-npm-3.4.12-9e2dc63475.patch",
+    "dompurify": "patch:dompurify@npm%3A3.4.13#~/.yarn/patches/dompurify-npm-3.4.13-71386e31f7.patch",
     "jest-process-manager/wait-on": "^9.0.5",
     "jsonpath-plus": "^10.3.0",
     "@metamask/jazzicon@npm:^2.0.0": "patch:@metamask/jazzicon@npm%3A2.0.0#~/.yarn/patches/@metamask-jazzicon-npm-2.0.0-36957be38d.patch",
@@ -513,7 +513,7 @@
     "cron-parser": "^4.5.0",
     "currency-formatter": "^1.4.2",
     "deep-freeze-strict": "1.1.1",
-    "dompurify": "patch:dompurify@npm%3A3.4.12#~/.yarn/patches/dompurify-npm-3.4.12-9e2dc63475.patch",
+    "dompurify": "patch:dompurify@npm%3A3.4.13#~/.yarn/patches/dompurify-npm-3.4.13-71386e31f7.patch",
     "eciesjs": "^0.5.0",
     "eth-chainlist": "~0.0.498",
     "eth-ens-namehash": "^2.0.8",
```

### yarn.lock
```diff
@@ -23838,27 +23838,27 @@ __metadata:
   languageName: node
   linkType: hard
 
-"dompurify@npm:3.4.12":
-  version: 3.4.12
-  resolution: "dompurify@npm:3.4.12"
+"dompurify@npm:3.4.13":
+  version: 3.4.13
+  resolution: "dompurify@npm:3.4.13"
   dependencies:
     "@types/trusted-types": "npm:^2.0.7"
   dependenciesMeta:
     "@types/trusted-types":
       optional: true
-  checksum: 10/f826b68920887eb75115a162facb42380d1c3fac441548217b30068c9fadeed14f63fa1f7a1d2ab6f63613e5a0f897aa245c9224d4abf7939cd8ae58c04646af
+  checksum: 10/0db0a309a868a38aca042f606b37446977c35ee4501850a8c1bf2781337d79871daf1f4344bbf5b545f2a8c62e4d4e192c8fd6f1ff49ecec7c865c55a0aefee3
   languageName: node
   linkType: hard
 
-"dompurify@patch:dompurify@npm%3A3.4.12#~/.yarn/patches/dompurify-npm-3.4.12-9e2dc63475.patch":
-  version: 3.4.12
-  resolution: "dompurify@patch:dompurify@npm%3A3.4.12#~/.yarn/patches/dompurify-npm-3.4.12-9e2dc63475.patch::version=3.4.12&hash=9e381f"
+"dompurify@patch:dompurify@npm%3A3.4.13#~/.yarn/patches/dompurify-npm-3.4.13-71386e31f7.patch":
+  version: 3.4.13
+  resolution: "dompurify@patch:dompurify@npm%3A3.4.13#~/.yarn/patches/dompurify-npm-3.4.13-71386e31f7.patch::version=3.4.13&hash=1f531d"
   dependencies:
     "@types/trusted-types": "npm:^2.0.7"
   dependenciesMeta:
     "@types/trusted-types":
       optional: true
-  checksum: 10/5c2883fc26371296c3357076f2cacad995901068a5b9f0ec6dccf7de9896818cc2e231b372efe769fb10c6e7c747c2c82a74a78e7e83764af4d2d2942b7a8737
+  checksum: 10/ae33e4915d6462d9faf52ae0922b3922b8d0dd7c29c8373f3c55da3fb2568bf38b58c3bb9df06f99070fea3df860338539a71b1e6e26404c4e31761db319a67b
   languageName: node
   linkType: hard
 
@@ -33068,7 +33068,7 @@ __metadata:
     deep-freeze-strict: "npm:1.1.1"
     depcheck: "npm:^1.4.7"
     detect-port: "npm:^1.5.1"
-    dompurify: "patch:dompurify@npm%3A3.4.12#~/.yarn/patches/dompurify-npm-3.4.12-9e2dc63475.patch"
+    dompurify: "patch:dompurify@npm%3A3.4.13#~/.yarn/patches/dompurify-npm-3.4.13-71386e31f7.patch"
     dotenv: "npm:^16.4.5"
     duplexify: "npm:^4.1.1"
     eciesjs: "npm:^0.5.0"
```
