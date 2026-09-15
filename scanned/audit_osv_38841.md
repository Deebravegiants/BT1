# [M] IRIS has an Excessive Data Exposure issue

## Summary
Severity: Medium
Advisory: CVE-2026-42539
Aliases: GHSA-g588-5gmf-p5cx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-42539
Type: osv

## Details
IRIS is a web collaborative platform that helps incident responders share technical details during investigations. Versions prior to 2.4.28 return sensitive data to the user which are not required for the client’s operation. Version 2.4.28 contains a patch.

## References
- http://www.openwall.com/lists/oss-security/2026/05/19/9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42539.json
- https://github.com/dfir-iris/iris-web/security/advisories/GHSA-g588-5gmf-p5cx
- https://nvd.nist.gov/vuln/detail/CVE-2026-42539
