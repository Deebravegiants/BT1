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
