# [H] Timing attack during remote cluster token comparison when shared channels are enabled

## Summary
Severity: High
Advisory: CVE-2024-39830
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/CVE-2024-39830
Type: osv

## Details
Mattermost versions 9.8.x <= 9.8.0, 9.7.x <= 9.7.4, 9.6.x <= 9.6.2 and 9.5.x <= 9.5.5, when shared channels are enabled, fail to use constant time comparison for remote cluster tokens which allows an attacker to retrieve the remote cluster token via a timing attack during remote cluster token comparison.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39830.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39830
