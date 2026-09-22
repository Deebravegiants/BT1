# [C] Path traversal in the aws:downloadContent plugin in amazon-ssm-agent

## Summary
Severity: Critical
Advisory: CVE-2026-81849
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-81849
Type: osv

## Details
Improper limitation of a pathname to a restricted directory in the aws:downloadContent plugin in amazon-ssm-agent before 3.3.4515.0 might allow an authenticated remote user whose ssm:SendCommand permission is restricted to the AWS-DownloadContent document, to write arbitrary files outside the intended download directory with root privileges, via crafted object keys in the S3 source the document is directed to retrieve. This issue may lead to arbitrary code execution as root if specific sensitive files are overwritten.



To remediate this issue, customers should upgrade amazon-ssm-agent to version 3.3.4515.0 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-091-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81849.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81849
- https://github.com/aws/amazon-ssm-agent/releases/tag/3.3.4515.0
