# [M] e107: Server-Side Request Forgery (SSRF) in the remote file fetcher

## Summary
Severity: Medium
Advisory: CVE-2026-43936
Aliases: GHSA-92fr-7h4f-22pp
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-43936
Type: osv

## Details
e107 is a content management system (CMS). Prior to 2.3.4, you can access the local environment by specifying the URL of the local environment from "Image/File URL:" of "From a remote location" in "Media Manager" on the administrator screen. This vulnerability is fixed in 2.3.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43936.json
- https://github.com/e107inc/e107/security/advisories/GHSA-92fr-7h4f-22pp
- https://nvd.nist.gov/vuln/detail/CVE-2026-43936
- https://github.com/e107inc/e107/commit/40b2d111
- https://github.com/e107inc/e107/commit/5f98cc9f
