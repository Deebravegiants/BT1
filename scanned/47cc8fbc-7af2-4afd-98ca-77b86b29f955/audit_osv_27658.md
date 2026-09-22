# [M] Bludit - Insecure Token Generation

## Summary
Severity: Medium
Advisory: CVE-2024-24554
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-24554
Type: osv

## Details
Bludit uses predictable methods in combination with the MD5 hashing algorithm to generate sensitive tokens such as the API token and the user token. This allows attackers to authenticate against the Bludit API.

## References
- https://github.com/bludit/bludit/
- https://www.bludit.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24554.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24554
- https://www.redguard.ch/blog/2024/06/20/security-advisory-bludit/
