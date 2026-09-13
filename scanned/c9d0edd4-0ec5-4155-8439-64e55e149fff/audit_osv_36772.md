# [C] ClipBucket v5 Affected by Remote Code Execution via Avatar/Background File Upload Race Condition

## Summary
Severity: Critical
Advisory: CVE-2026-25728
Aliases: GHSA-xq7c-m5r2-9wqj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2026-25728
Type: osv

## Details
ClipBucket v5 is an open source video sharing platform. Prior to 5.5.3 - #40, a Time-of-Check to Time-of-Use (TOCTOU) race condition vulnerability exists in ClipBucket's avatar and background image upload functionality. The application moves uploaded files to a web-accessible location before validating them, creating a window where an attacker can execute arbitrary PHP code before the file is deleted. The uploaded file was moved to a web-accessible path via move_uploaded_file(), then validated via ValidateImage(). If validation failed, the file was deleted via @unlink(). This vulnerability is fixed in 5.5.3 - #40.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25728.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-xq7c-m5r2-9wqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-25728
- https://github.com/MacWarrior/clipbucket-v5/commit/09536e6e2ca6d69a2ee83190b588c0b8116dd16d
