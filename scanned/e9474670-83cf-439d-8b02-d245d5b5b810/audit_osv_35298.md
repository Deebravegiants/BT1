# [C] CVE-2025-70833

## Summary
Severity: Critical
Advisory: CVE-2025-70833
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2025-70833
Type: osv

## Details
An Authentication Bypass vulnerability in Smanga 3.2.7 allows an unauthenticated attacker to reset the password of any user (including the administrator) and fully takeover the account by manipulating POST parameters. The issue stems from insecure permission validation in check-power.php.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70833.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70833
- https://github.com/LX-66-LX/cve/issues/4
