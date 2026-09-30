# [C] CVE-2024-45321

## Summary
Severity: Critical
Advisory: CVE-2024-45321
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-27
Source: https://osv.dev/vulnerability/CVE-2024-45321
Type: osv

## Details
The App::cpanminus package through 1.7047 for Perl downloads code via insecure HTTP, enabling code execution for network attackers.

## References
- https://security.metacpan.org/2024/08/26/cpanminus-downloads-code-using-insecure-http.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45321.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45321
- https://github.com/miyagawa/cpanminus/issues/611
- https://github.com/miyagawa/cpanminus/pull/674
