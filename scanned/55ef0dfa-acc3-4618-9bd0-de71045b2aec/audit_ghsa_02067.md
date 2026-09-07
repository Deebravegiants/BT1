# [H] Calipso Arbitrary File Write via Archive Extraction (Zip Slip)

## Summary
Severity: High
Advisory: GHSA-jxcc-g75x-qgw9
CVE: CVE-2021-23391
CWE: CWE-29, CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-jxcc-g75x-qgw9
Type: github-advisory

## Affected
- npm: `calipso` — affected >=0

## Details
This affects all versions of package calipso. It is possible for a malicious module to overwrite files on an arbitrary file system through the module install functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23391
- https://github.com/cliftonc/calipso
- https://snyk.io/vuln/SNYK-JS-CALIPSO-1300555
