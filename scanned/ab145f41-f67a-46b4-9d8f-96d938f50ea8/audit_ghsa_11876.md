# [M] Craft CMS Vulnerable to Stored XSS in Revision Context Menu

## Summary
Severity: Medium
Advisory: GHSA-3x4w-mxpf-fhqq
CVE: CVE-2026-33051
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-3x4w-mxpf-fhqq
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.9.0-beta.1 <5.9.11

## Details
The revision/draft context menu in the element editor renders the creator’s `fullName` as raw HTML due to the 
use of `Template::raw()` combined with `Craft::t()` string interpolation. A low-privileged control panel user
(e.g., Author) can set their fullName to an XSS payload via the profile editor, then create an entry with two
saves.

If an administrator is logged in and executes a specifically crafted payload while an elevated session is active, the attacker’s account can be elevated to administrator.

Users should update to Craft 5.9.11 with the patch to mitigate the issue.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-3x4w-mxpf-fhqq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33051
- https://github.com/craftcms/cms/commit/f634a9d21edcafd83a6716047d275f985aba6be1
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/5.9.11
