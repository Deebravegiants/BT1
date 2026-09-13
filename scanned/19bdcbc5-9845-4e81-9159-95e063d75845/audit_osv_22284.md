# [M] Path Traversal in OpenClinica

## Summary
Severity: Medium
Advisory: CVE-2022-24830
Aliases: GHSA-9rrv-prff-qph7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-05-13
Source: https://osv.dev/vulnerability/CVE-2022-24830
Type: osv

## Details
OpenClinica is an open source software for Electronic Data Capture (EDC) and Clinical Data Management (CDM). OpenClinica prior to version 3.16 is vulnerable to path traversal in multiple endpoints, leading to arbitrary file read/write, and potential remote code execution. There are no known workarounds. This issue has been patched and users are recommended to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24830.json
- https://github.com/OpenClinica/OpenClinica/security/advisories/GHSA-9rrv-prff-qph7
- https://nvd.nist.gov/vuln/detail/CVE-2022-24830
- https://github.com/OpenClinica/OpenClinica/commit/6f864e86543f903bd20d6f9fc7056115106441f3
