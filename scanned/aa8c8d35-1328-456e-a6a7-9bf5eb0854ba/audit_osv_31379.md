# [H] ShowDoc < 2.8.7 Unauthenticated File Upload Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2025-0520
Aliases: GHSA-6jmr-r7p6-f5wr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:H/SI:H/SA:L)
Published: 2025-04-29
Source: https://osv.dev/vulnerability/CVE-2025-0520
Type: osv

## Details
An unrestricted file upload vulnerability in ShowDoc caused by improper validation of file extension allows execution of arbitrary PHP, leading to remote code execution.This issue affects ShowDoc: before 2.8.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0520.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0520
- https://www.cnvd.org.cn/flaw/show/CNVD-2020-26585
- https://www.vulncheck.com/advisories/showdoc-unauthenticated-file-upload-rce
- https://github.com/star7th/showdoc/pull/1059
- https://github.com/vulhub/vulhub/tree/master/showdoc/CNVD-2020-26585
