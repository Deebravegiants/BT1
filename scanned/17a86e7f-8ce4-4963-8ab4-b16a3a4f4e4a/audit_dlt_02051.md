# [?] fix: bump `fast-xml-parser` to `5.3.6` to fix DoS vulnerability and ignore `ajv` advisory (#40187)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-02-18
Source: https://github.com/MetaMask/metamask-extension/commit/a6f0d07f373c23a0ba8912ce2ecd1fc26e15d68d
Type: security-commit

## Details
fix: bump `fast-xml-parser` to `5.3.6` to fix DoS vulnerability and ignore `ajv` advisory (#40187)

## **Description**

Bumps the
[`fast-xml-parser`](https://github.com/NaturalIntelligence/fast-xml-parser/blob/master/CHANGELOG.md)
yarn resolution from `^5.3.4` to `^5.3.6` to resolve a high-severity DoS
vulnerability caused by unrestricted entity expansion in DOCTYPE
parsing.

- **Reason:** `fast-xml-parser` versions `>=4.1.3 <5.3.6` are affected
by
[GHSA-jmr7-xgp7-cmfj](https://github.com/advisories/GHSA-jmr7-xgp7-cmfj).
- **Solution:** Bump the resolution override to `^5.3.6`, the first
patched version. The vulnerable dependency is pulled in transitively via
`@metamask/snaps-utils@12.1.0`.

Also ignores `ajv` advisory since it does not impact production and is
hard to update.

## **Changelog**

CHANGELOG entry: null

## **Related issues**

Fixes: https://github.com/advisories/GHSA-jmr7-xgp7-cmfj

## **Manual testing steps**

1. Run `yarn audit` and verify `fast-xml-parser` and `ajv` no longer
appears as vulnerable.
2. Run `yarn install` and confirm no resolution errors.

## **Screenshots/Recordings**

### **Before**

<!-- N/A - dependency version bump only -->

### **After**

<!-- N/A - dependency version bump only -->

## **Pre-merge author checklist**

- [x] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [x] I've completed the PR template to the best of my ability
- [ ] I've included tests if applicable
- [ ] I've documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [ ] I've applied the right labels on the PR (see [labeling
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
> Primarily a dependency patch-level bump plus lockfile update; low
runtime risk, with the main concern being potential knock-on behavior
changes in XML parsing or tooling due to the upgraded transitive
dependency.
> 
> **Overview**
> Updates the Yarn `resolutions` override for `fast-xml-parser` from
`^5.3.4` to `^5.3.6` (and updates `yarn.lock`, including the transitive
`strnum` version) to pick up upstream DoS fixes.
> 
> Separately adds an `npmAuditIgnoreAdvisories` entry for an `ajv` ReDoS
advisory to unblock CI for tooling that still depends on older `ajv`
versions.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
28a65c3192ab43138f1f29a4f91f27c2f0a09d5b. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

---------

Co-authored-by: Frederik Bolding <frederik.bolding@gmail.com>

### .yarnrc.yml
```diff
@@ -37,6 +37,12 @@ npmAuditIgnoreAdvisories:
   # URL: https://github.com/advisories/GHSA-wqch-xfxh-vrr4
   - 1110857
 
+  # Issue: ajv has ReDoS when using `$data` option
+  # A lot of our linting tooling relies on old versions of ajv, which proves hard to deal with
+  # For now, we are ignoring this to unblock CI
+  # URL: https://github.com/advisories/GHSA-2g4f-4pwh-qvx6
+  - 1113214
+
   ### Package Deprecations:
 
   # React-tippy brings in popper.js and react-tippy has not been updated in
```

### package.json
```diff
@@ -249,7 +249,7 @@
     "qs@npm:6.13.0": "^6.14.1",
     "@metamask/bridge-status-controller": "64.3.0",
     "@ledgerhq/hw-transport-webhid@npm:^6.31.0": "patch:@ledgerhq/hw-transport-webhid@npm%3A6.31.0#~/.yarn/patches/@ledgerhq-hw-transport-webhid-npm-6.31.0-efbecf27ab.patch",
-    "fast-xml-parser": "^5.3.4",
+    "fast-xml-parser": "^5.3.6",
     "@metamask/snaps-controllers": "^18.0.0"
   },
   "dependencies": {
```

### yarn.lock
```diff
@@ -26411,14 +26411,14 @@ __metadata:
   languageName: node
   linkType: hard
 
-"fast-xml-parser@npm:^5.3.4":
-  version: 5.3.4
-  resolution: "fast-xml-parser@npm:5.3.4"
+"fast-xml-parser@npm:^5.3.6":
+  version: 5.3.6
+  resolution: "fast-xml-parser@npm:5.3.6"
   dependencies:
-    strnum: "npm:^2.1.0"
+    strnum: "npm:^2.1.2"
   bin:
     fxparser: src/cli/cli.js
-  checksum: 10/0d7e6872fed7c3065641400d43cdf24c03177f05c343bfb31df53b79f0900b085c103f647852d0b00693125aa3f0e9d8b8cfc4273b168d4da0308f857dafe830
+  checksum: 10/03527ab0bdf49d960fdc8f6088cd0715c052e06b68b39459da87b1a1fbb3439a855b2d83cbf3c400e983b8e668b396296b072a4dd5c63403cf1e618c9326b6df
   languageName: node
   linkType: hard
 
@@ -42143,7 +42143,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"strnum@npm:^2.1.0":
+"strnum@npm:^2.1.2":
   version: 2.1.2
   resolution: "strnum@npm:2.1.2"
   checksum: 10/7d894dff385e3a5c5b29c012cf0a7ea7962a92c6a299383c3d6db945ad2b6f3e770511356a9774dbd54444c56af1dc7c435dad6466c47293c48173274dd6c631
```
