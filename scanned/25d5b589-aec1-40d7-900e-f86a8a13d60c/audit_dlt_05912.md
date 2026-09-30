# [?] chore: bump basic-ftp to 5.3.1 to fix GHSA-rpmf-866q-6p89 (#42508)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-05-11
Source: https://github.com/MetaMask/metamask-extension/commit/97d72eb35423c9851b63cfbe5940fe67ab500f80
Type: security-commit

## Details
chore: bump basic-ftp to 5.3.1 to fix GHSA-rpmf-866q-6p89 (#42508)

`basic-ftp@5.3.0` is vulnerable to client-side DoS (GHSA-rpmf-866q-6p89,
high): a malicious FTP server can send an unterminated multiline banner,
causing the client to buffer and reparse unbounded attacker-controlled
data, exhausting memory/CPU. This is a dev-only transitive dependency.

## Changes

- **`package.json`**: Added `"basic-ftp": "^5.3.1"` to `resolutions` to
pin to the patched release
- **`yarn.lock`**: Updated `basic-ftp` from `5.3.0` → `5.3.1`

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk lockfile-only dependency bump to a patch release; primary
impact is on build/dev tooling dependency resolution.
> 
> **Overview**
> Updates the `yarn.lock` entry for `basic-ftp` from `5.3.0` to `5.3.1`,
pulling in the patched version referenced by GHSA-rpmf-866q-6p89.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit
93e016445f764174ffbe0bbc0169eec42cea1dfe. Bugbot is set up for automated
code reviews on this repo. Configure
[here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: DDDDDanica <12678455+DDDDDanica@users.noreply.github.com>
Co-authored-by: dddddanica <zhaodanica@gmail.com>

## Patch
### yarn.lock
```diff
@@ -20240,9 +20240,9 @@ __metadata:
   linkType: hard
 
 "basic-ftp@npm:^5.0.2":
-  version: 5.3.0
-  resolution: "basic-ftp@npm:5.3.0"
-  checksum: 10/08eef717642f32d92936e02f516ab6426ecc61084e4a75b542cd202dd84dddff2520dda321db1be34b7e49860cf1b2aed67ab275dc3e53b185949df311241396
+  version: 5.3.1
+  resolution: "basic-ftp@npm:5.3.1"
+  checksum: 10/9232ee155114efafadf5adee86a6750208653a9071e53e9803dceac61a66b3ba3974771ff2490ff28f1a118fdfb806ffcc488f64609e61a9cedb52480b312843
   languageName: node
   linkType: hard
 
```
