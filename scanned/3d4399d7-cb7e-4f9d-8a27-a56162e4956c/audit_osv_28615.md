# [M] CVE-2024-35539

## Summary
Severity: Medium
Advisory: CVE-2024-35539
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-08-19
Source: https://osv.dev/vulnerability/CVE-2024-35539
Type: osv

## Details
Typecho v1.3.0 was discovered to contain a race condition vulnerability in the post commenting function. This vulnerability allows attackers to post several comments before the spam protection checks if the comments are posted too frequently.

## References
- https://cyberaz0r.info/2024/08/typecho-multiple-vulnerabilities/
- https://typecho.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35539.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35539
