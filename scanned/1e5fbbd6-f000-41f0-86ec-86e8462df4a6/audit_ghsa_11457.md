# [M] Connect CMS has SSRF in the External Page Migration Feature of its Page Management Plugin

## Summary
Severity: Medium
Advisory: GHSA-jh46-85jr-6ph9
CVE: CVE-2026-32279
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-jh46-85jr-6ph9
Type: github-advisory

## Affected
- Packagist: `opensource-workshop/connect-cms` — affected >=0 <1.41.1
- Packagist: `opensource-workshop/connect-cms` — affected >=2.0.0 <2.41.1

## Details
# Security Advisory — Page Management Plugin (SSRF)

## Summary

A Server-Side Request Forgery (SSRF) issue exists in the external page migration feature of the Page Management Plugin.

## Affected Versions

- 1.x series: <= 1.41.0
- 2.x series: <= 2.41.0

## Patched Versions

- 1.41.1
- 2.41.1

## Description

In the external page migration feature of the Page Management Plugin, a Server-Side Request Forgery (SSRF) issue could occur. If exploited, it may allow access to internal destinations and could result in information disclosure. Exploitation requires privileges that allow use of the page management screen. Users affected by this vulnerability should update to a fixed version.

## Solution

Update to the fixed version.
For the 1.x series, update to 1.41.1 or later.
For the 2.x series, update to 2.41.1 or later.

## Credits

OpenSource WorkShop thanks **Sho Odagiri** (小田切 祥) of **GMO Cybersecurity by Ierae, Inc.** for reporting this vulnerability.

## References
- https://github.com/opensource-workshop/connect-cms/security/advisories/GHSA-jh46-85jr-6ph9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32279
- https://github.com/opensource-workshop/connect-cms/commit/4a1a64a8f768a53e06a4239e25782d9e2e88fc63
- https://github.com/opensource-workshop/connect-cms/commit/617a874e14b8476da7c0760a06384b9da21bdd4f
- https://github.com/opensource-workshop/connect-cms
- https://github.com/opensource-workshop/connect-cms/releases/tag/v1.41.1
- https://github.com/opensource-workshop/connect-cms/releases/tag/v2.41.1
