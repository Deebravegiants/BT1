# [M] juzaweb CMS allows cross-site scripting by uploading an SVG file

## Summary
Severity: Medium
Advisory: GHSA-49rr-34j5-r8mw
CVE: CVE-2025-5420
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-06-02
Source: https://github.com/advisories/GHSA-49rr-34j5-r8mw
Type: github-advisory

## Affected
- Packagist: `juzaweb/cms` — affected >=0

## Details
A vulnerability classified as problematic was found in juzaweb CMS up to 3.4.2. Affected by this vulnerability is an unknown functionality of the file /admin-cp/file-manager/upload of the component Profile Page. The manipulation of the argument Upload leads to cross site scripting. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5420
- https://github.com/Cyber-Wo0dy/report/blob/main/juzawebcms/3.4.2/juzawebcms_avatar_xss.md
- https://github.com/juzaweb/cms
- https://vuldb.com/?ctiid.310753
- https://vuldb.com/?id.310753
- https://vuldb.com/?submit.584048
