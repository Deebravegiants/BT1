# [H] Zip Slip Arbitrary File Write in AWS diagram-as-code (awsdac)

## Summary
Severity: High
Advisory: CVE-2026-81838
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81838
Type: osv

## Details
A relative path traversal issue in the zip extraction functionality in AWS diagram-as-code (awsdac) in versions 0.10 through 0.23 can allow a third party to write arbitrary files to the local filesystem via crafted zip entry names containing path traversal sequences. This could allow the third party to perform inappropriate actions in the diagram bundle.



To remediate this issue, users should upgrade to the version 0.24 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-090-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81838.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81838
- https://github.com/awslabs/diagram-as-code/releases/tag/v0.24
