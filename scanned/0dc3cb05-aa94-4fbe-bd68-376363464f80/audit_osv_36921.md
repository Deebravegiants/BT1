# [M] Ghostty affected by arbitrary command execution via control characters in paste and drag-and-drop operations

## Summary
Severity: Medium
Advisory: CVE-2026-26982
Aliases: GHSA-4jxv-xgrp-5m3r
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2026-26982
Type: osv

## Details
Ghostty is a cross-platform terminal emulator. Ghostty allows control characters such as 0x03 (Ctrl+C) in pasted and dropped text. These can be used to execute arbitrary commands in some shell environments. This attack requires an attacker to convince the user to copy and paste or drag and drop malicious text. The attack requires user interaction to be triggered, but the dangerous characters are invisible in most GUI environments so it isn't trivially detected, especially if the string contents are complex. Fixed in Ghostty v1.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26982.json
- https://github.com/ghostty-org/ghostty/security/advisories/GHSA-4jxv-xgrp-5m3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-26982
- https://github.com/ghostty-org/ghostty/commit/fe7427ed2a1a02aef85495b384cfb8f11ee5efc9
- https://github.com/ghostty-org/ghostty/pull/10746
