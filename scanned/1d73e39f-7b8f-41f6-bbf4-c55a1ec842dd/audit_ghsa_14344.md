# [M] Cross-site scripting vulnerabilities in old version of bundled TinyMCE

## Summary
Severity: Medium
Advisory: GHSA-wqm8-jx8r-8rcq
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-wqm8-jx8r-8rcq
Type: github-advisory

## Affected
- Packagist: `silverstripe/admin` — affected >=0 <1.12.7

## Details
An old version of TinyMCE include an XSS vulnerability, which was patched in a later version. This was described by TinyMCE:

> A cross-site scripting (XSS) vulnerability was discovered in the core parser. The vulnerability allowed arbitrary JavaScript execution when inserting a specially crafted piece of content into the editor via the clipboard or APIs. This impacts all users who are using TinyMCE 4.9.10 or lower and TinyMCE 5.4.0 or lower.

We reviewed the potential impact of this vulnerability within the context of Silverstripe CMS. We concluded this is a medium impact vulnerability given how TinyMCE is used by Silverstripe CMS.

Reported by: Developers at ACC

## References
- https://github.com/silverstripe/silverstripe-admin/security/advisories/GHSA-wqm8-jx8r-8rcq
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/admin/SS-2023-001.yaml
- https://github.com/advisories/GHSA-vrv8-v4w8-f95h
- https://github.com/silverstripe/silverstripe-admin
- https://www.silverstripe.org/download/security-releases/ss-2023-001
- https://www.tiny.cloud/docs/release-notes/release-notes54/#securityfixes
