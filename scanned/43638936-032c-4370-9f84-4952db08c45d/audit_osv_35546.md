# [M] HTTPS Fallback to HTTP in Graph Explorer

## Summary
Severity: Medium
Advisory: CVE-2026-10584
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-10584
Type: osv

## Details
Proxy server in Graph Explorer before 3.0.1 falls back to HTTP when certificate files are missing, which might allow remote threat actors to obtain sensitive information via interception of requests intended to be sent over HTTPS.



To remediate this issue, users should upgrade to Graph Explorer v3.0.1 or later.

## References
- https://aws.amazon.com/security/security-bulletins/2026-038-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10584.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10584
- https://github.com/aws/graph-explorer/releases/tag/v3.0.1
