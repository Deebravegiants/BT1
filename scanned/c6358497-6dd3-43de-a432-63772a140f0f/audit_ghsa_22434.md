# [M] Showdoc Forced Browsing

## Summary
Severity: Medium
Advisory: GHSA-6xx7-cphv-pxgr
CVE: CVE-2018-19609
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6xx7-cphv-pxgr
Type: github-advisory

## Affected
- Packagist: `showdoc/showdoc` — affected >=0

## Details
ShowDoc 2.4.1 allows remote attackers to obtain sensitive information by navigating with a modified page_id, as demonstrated by reading note content, or discovering a username in the JSON data at a diff URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19609
- https://github.com/CCCCCrash/POCs/tree/master/Web/showdoc/IncorrectAccessControl
- https://github.com/star7th/showdoc
