# [C] Heap double-free in AWS Common Runtime aws-c-http

## Summary
Severity: Critical
Advisory: CVE-2026-12043
Aliases: GHSA-rmjr-3qpm-vh98
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-12043
Type: osv

## Details
Improper handling of HPACK dynamic table size updates in the AWS Common Runtime aws-c-http library might allow a remote threat actor operating a server to cause memory corruption on a connecting client application, potentially leading to arbitrary code execution, via a crafted sequence of HTTP/2 HEADERS frames.



To remediate this issue, users should upgrade to aws-c-http version 0.11.0.

## References
- https://aws.amazon.com/security/security-bulletins/2026-043-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12043.json
- https://github.com/awslabs/aws-c-http/security/advisories/GHSA-rmjr-3qpm-vh98
- https://nvd.nist.gov/vuln/detail/CVE-2026-12043
- https://github.com/awslabs/aws-c-http/releases/tag/v0.11.0
