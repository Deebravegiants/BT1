# [H] Connect-CMS has Arbitrary Code Execution by an Authenticated User in its Code Study Plugin

## Summary
Severity: High
Advisory: GHSA-hxqw-6qv7-cqfv
CVE: CVE-2026-32276
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-hxqw-6qv7-cqfv
Type: github-advisory

## Affected
- Packagist: `opensource-workshop/connect-cms` — affected >=0 <1.41.1
- Packagist: `opensource-workshop/connect-cms` — affected >=2.0.0 <2.41.1

## Details
# Security Advisory — Code Study Plugin

## Summary

An authenticated user may be able to execute arbitrary code in the Code Study Plugin.

## Affected Versions

- 1.x series: <= 1.41.0
- 2.x series: <= 2.41.0

## Patched Versions

- 1.41.1
- 2.41.1

## Description

In the Code Study Plugin, an authenticated user could trigger unintended code execution. If exploited, it may lead to code execution on the server or information disclosure. Users affected by this vulnerability should update to a fixed version.

## Solution

Update to the fixed version.
For the 1.x series, update to 1.41.1 or later.
For the 2.x series, update to 2.41.1 or later.

## Credits

OpenSource WorkShop thanks **Sho Odagiri** (小田切 祥) of **GMO Cybersecurity by Ierae, Inc.** for reporting this vulnerability.

## References
- https://github.com/opensource-workshop/connect-cms/security/advisories/GHSA-hxqw-6qv7-cqfv
- https://nvd.nist.gov/vuln/detail/CVE-2026-32276
- https://github.com/opensource-workshop/connect-cms/commit/c0bcd07fc1e9375941aa1295d044328ecd44ed85
- https://github.com/opensource-workshop/connect-cms
- https://github.com/opensource-workshop/connect-cms/releases/tag/v1.41.1
- https://github.com/opensource-workshop/connect-cms/releases/tag/v2.41.1
