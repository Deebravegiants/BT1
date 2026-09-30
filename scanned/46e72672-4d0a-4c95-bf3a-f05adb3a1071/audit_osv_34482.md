# [M] CVE-2025-60798

## Summary
Severity: Medium
Advisory: CVE-2025-60798
Aliases: GHSA-g6xh-wrpf-v6j6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-20
Source: https://osv.dev/vulnerability/CVE-2025-60798
Type: osv

## Details
phpPgAdmin 7.13.0 and earlier contains a SQL injection vulnerability in display.php at line 396. The application passes user-controlled input from $_REQUEST['query'] directly to the browseQuery function without proper sanitization. An authenticated attacker can exploit this vulnerability to execute arbitrary SQL commands through malicious query manipulation, potentially leading to complete database compromise.

## References
- https://github.com/phppgadmin/phppgadmin/blob/master/display.php#L396
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60798.json
- https://github.com/pr0wl1ng/security-advisories/blob/main/CVE-2025-60797.md
- https://github.com/pr0wl1ng/security-advisories/blob/main/CVE-2025-60798.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-60798
