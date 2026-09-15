# [M] Brute-force protection ineffective for some login methods

## Summary
Severity: Medium
Advisory: CVE-2024-28825
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-04-24
Source: https://osv.dev/vulnerability/CVE-2024-28825
Type: osv

## Details
Improper restriction of excessive authentication attempts on some authentication methods in Checkmk before 2.3.0b5 (beta), 2.2.0p26, 2.1.0p43, and in Checkmk 2.0.0 (EOL) facilitates password brute-forcing.

## References
- https://checkmk.com/werk/15198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28825.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-28825
