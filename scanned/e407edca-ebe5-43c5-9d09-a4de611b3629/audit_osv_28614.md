# [M] CVE-2024-35538

## Summary
Severity: Medium
Advisory: CVE-2024-35538
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-08-19
Source: https://osv.dev/vulnerability/CVE-2024-35538
Type: osv

## Details
Typecho v1.3.0 was discovered to contain a Client IP Spoofing vulnerability, which allows attackers to falsify their IP addresses by specifying an arbitrary IP as value of X-Forwarded-For or Client-Ip headers while performing HTTP requests.

## References
- https://cyberaz0r.info/2024/08/typecho-multiple-vulnerabilities/
- https://typecho.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35538.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35538
