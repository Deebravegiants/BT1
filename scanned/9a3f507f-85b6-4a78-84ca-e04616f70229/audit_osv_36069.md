# [M] Out-of-bounds write in the Base64 decoder in Amazon aws-sdk-cpp

## Summary
Severity: Medium
Advisory: CVE-2026-19642
Aliases: GHSA-wxx3-prfc-69xx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-19642
Type: osv

## Details
An out-of-bounds write issue in the Base64 decoder in Amazon aws-sdk-cpp before 1.11.862 might allow a remote authenticated user to cause a crash or heap memory corruption in an application that processes crafted Base64-encoded input.



To remediate this issue, users should upgrade to version 1.11.862.

## References
- https://aws.amazon.com/security/security-bulletins/2026-080-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19642.json
- https://github.com/aws/aws-sdk-cpp/security/advisories/GHSA-wxx3-prfc-69xx
- https://nvd.nist.gov/vuln/detail/CVE-2026-19642
- https://github.com/aws/aws-sdk-cpp/releases/tag/1.11.862
