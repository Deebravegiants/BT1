# [M] Cross-site Scripting in MobileDetect

## Summary
Severity: Medium
Advisory: GHSA-r77c-qv68-j3pp
CVE: CVE-2018-25080
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-04
Source: https://github.com/advisories/GHSA-r77c-qv68-j3pp
Type: github-advisory

## Affected
- Packagist: `mobiledetect/mobiledetectlib` — affected >=0 <2.8.32

## Details
A vulnerability, which was classified as problematic, has been found in MobileDetect 2.8.31. This issue affects the function initLayoutType of the file examples/session_example.php of the component Example. The manipulation of the argument $_SERVER['PHP_SELF'] leads to cross site scripting. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 2.8.32 is able to address this issue. The name of the patch is 31818a441b095bdc4838602dbb17b8377d1e5cce. It is recommended to upgrade the affected component. The identifier VDB-220061 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25080
- https://github.com/serbanghita/Mobile-Detect/pull/741
- https://github.com/serbanghita/Mobile-Detect/commit/31818a441b095bdc4838602dbb17b8377d1e5cce
- https://github.com/MarkLee131/awesome-web-pocs/blob/main/CVE-2018-25080.md
- https://github.com/serbanghita/Mobile-Detect
- https://github.com/serbanghita/Mobile-Detect/releases/tag/2.8.32
- https://vuldb.com/?ctiid.220061
- https://vuldb.com/?id.220061
