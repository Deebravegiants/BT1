# [H] Connect CMS: Information Disclosure Due to Improper Authorization through the Page Content Retrieval Feature

## Summary
Severity: High
Advisory: GHSA-62ch-j6x7-722j
CVE: CVE-2026-32299
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-62ch-j6x7-722j
Type: github-advisory

## Affected
- Packagist: `opensource-workshop/connect-cms` — affected >=0 <1.41.1
- Packagist: `opensource-workshop/connect-cms` — affected >=2.0.0 <2.41.1

## Details
# Security Advisory — Page Content Retrieval (Improper Authorization)

## Summary

An improper authorization issue in the page content retrieval feature may allow retrieval of non-public information.

## Affected Versions

- 1.x series: <= 1.41.0
- 2.x series: <= 2.41.0

## Patched Versions

- 1.41.1
- 2.41.1

## Description

In part of the page content retrieval feature, insufficient authorization checks could allow processing associated with non-public pages to be executed. If exploited, the contents and attachments of non-public pages may be obtained by a third party. Users affected by this vulnerability should update to a fixed version.

## Solution

Update to the fixed version.
For the 1.x series, update to 1.41.1 or later.
For the 2.x series, update to 2.41.1 or later.

## Credits

OpenSource WorkShop thanks **Sho Odagiri** (小田切 祥) of **GMO Cybersecurity by Ierae, Inc.** for reporting this vulnerability.

## References
- https://github.com/opensource-workshop/connect-cms/security/advisories/GHSA-62ch-j6x7-722j
- https://nvd.nist.gov/vuln/detail/CVE-2026-32299
- https://github.com/opensource-workshop/connect-cms
- https://github.com/opensource-workshop/connect-cms/releases/tag/v1.41.1
- https://github.com/opensource-workshop/connect-cms/releases/tag/v2.41.1
