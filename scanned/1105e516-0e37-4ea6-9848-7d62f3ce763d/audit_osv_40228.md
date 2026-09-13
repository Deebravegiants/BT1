# [C] AWS C Event Stream Streaming Decoder Stack Buffer Overflow

## Summary
Severity: Critical
Advisory: CVE-2026-5190
Aliases: GHSA-xvjw-fjq5-68hf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-5190
Type: osv

## Details
Out-of-bounds write in the streaming decoder component in aws-c-event-stream before 0.6.0 might allow a third party operating a server to cause memory corruption leading to arbitrary code execution on a client application that processes crafted event-stream messages.

To remediate this issue, users should upgrade to version 0.6.0 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-011-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5190.json
- https://github.com/awslabs/aws-c-event-stream/security/advisories/GHSA-xvjw-fjq5-68hf
- https://nvd.nist.gov/vuln/detail/CVE-2026-5190
- https://github.com/awslabs/aws-c-event-stream/releases/tag/v0.6.0
