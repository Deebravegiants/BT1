# [C] Arbitrary Code Execution via Sandbox Bypass in the open source solution QnABot on AWS

## Summary
Severity: Critical
Advisory: CVE-2026-7191
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/CVE-2026-7191
Type: osv

## Details
Improper use of the static-eval npm package in the open source solution qnabot-on-aws versions 7.2.4 and earlier may allow an authenticated administrator to execute arbitrary code within the fulfillment Lambda execution context by injecting a crafted conditional chaining expression via the Content Designer interface, which bypasses the intended expression sandbox through JavaScript prototype manipulation. This may grant direct access to backend resources (Lambda environment variables, OpenSearch indices, S3 objects, DynamoDB tables) that are not exposed through normal administrative interfaces.

We recommend you upgrade to version 7.3.0 or above.

## References
- https://aws.amazon.com/security/security-bulletins/2026-020-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7191.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-7191
- https://github.com/aws-solutions/qnabot-on-aws/releases/tag/v7.3.0
