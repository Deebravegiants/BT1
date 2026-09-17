# [H] Session Hijacking via token exposure on the session page in Xibo CMS

## Summary
Severity: High
Advisory: CVE-2024-29023
Aliases: GHSA-xmc6-cfq5-hg39
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-12
Source: https://osv.dev/vulnerability/CVE-2024-29023
Type: osv

## Details
Xibo is an Open Source Digital Signage platform with a web content management system and Windows display player software. Session tokens are exposed in the return of session search API call on the sessions page. Subsequently they can be exfiltrated and used to hijack a session. Users must be granted access to the session page, or be a super admin. Users should upgrade to version 3.3.10 or 4.0.9 which fix this issue. Customers who host their CMS with the Xibo Signage service have already received an upgrade or patch to resolve this issue regardless of the CMS version that they are running. Patches are available for earlier versions of Xibo CMS that are out of security support: 2.3 patch ebeccd000b51f00b9a25f56a2f252d6812ebf850.diff. 1.8 patch a81044e6ccdd92cc967e34c125bd8162432e51bc.diff. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29023.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-xmc6-cfq5-hg39
- https://nvd.nist.gov/vuln/detail/CVE-2024-29023
- https://xibosignage.com/blog/security-advisory-2024-04
- https://github.com/dasgarner/xibo-cms/commit/a81044e6ccdd92cc967e34c125bd8162432e51bc.diff
- https://github.com/xibosignage/xibo-cms/commit/3b93636aa7aea07d1f7dfa36b63b773ac16d7cde
- https://github.com/xibosignage/xibo-cms/commit/49f018fd9fe64fcd417d7c2ef96078bd7b2b88b7
- https://github.com/xibosignage/xibo-cms/commit/ebeccd000b51f00b9a25f56a2f252d6812ebf850.diff
