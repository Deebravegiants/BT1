# [C] tinymighty WikiSEO is vulnerable to cross-site scripting via modifyHTML function

## Summary
Severity: Critical
Advisory: GHSA-84mm-prjg-49xm
CVE: CVE-2015-10073
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-06
Source: https://github.com/advisories/GHSA-84mm-prjg-49xm
Type: github-advisory

## Affected
- Packagist: `tinymighty/wiki-seo` — affected >=0 <1.2.2

## Details
A vulnerability was found in tinymighty WikiSEO 1.2.1. This affects the function modifyHTML of the file WikiSEO.body.php of the component Meta Property Tag Handler. The manipulation of the argument content leads to cross site scripting. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 1.2.2 is able to address this issue. The name of the patch is 089a5797be612b18a820f9f1e6593ad9a91b1dba. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-220215.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10073
- https://github.com/tinymighty/wiki-seo/pull/21
- https://github.com/tinymighty/wiki-seo/commit/089a5797be612b18a820f9f1e6593ad9a91b1dba
- https://github.com/tinymighty/wiki-seo
- https://github.com/tinymighty/wiki-seo/releases/tag/1.2.2
- https://vuldb.com/?ctiid.220215
- https://vuldb.com/?id.220215
