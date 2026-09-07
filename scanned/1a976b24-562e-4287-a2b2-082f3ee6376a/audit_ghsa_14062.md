# [M] SSCMS vulnerable to Cross Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-63c6-w556-3h7q
CVE: CVE-2023-2862
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-63c6-w556-3h7q
Type: github-advisory

## Affected
- NuGet: `SSCMS` — affected >=0

## Details
A vulnerability, which was classified as problematic, was found in SiteServer CMS up to 7.2.1. Affected is an unknown function of the file `/api/stl/actions/search`. The manipulation of the argument ajaxDivId leads to cross site scripting. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. It is recommended to apply a patch to fix this issue. VDB-229818 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2862
- https://gitee.com/siteserver/cms
- https://gitee.com/siteserver/cms/issues/I71WJ4
- https://vuldb.com/?ctiid.229818
- https://vuldb.com/?id.229818
