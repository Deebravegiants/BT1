# [H] CVE-2023-52159

## Summary
Severity: High
Advisory: CVE-2023-52159
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2023-52159
Type: osv

## Details
A stack-based buffer overflow vulnerability in gross 0.9.3 through 1.x before 1.0.4 allows remote attackers to trigger a denial of service (grossd daemon crash) or potentially execute arbitrary code in grossd via crafted SMTP transaction parameters that cause an incorrect strncat for a log entry.

## References
- https://codeberg.org/bizdelnick/gross/wiki/Known-vulnerabilities#cve-2023-52159
- https://lists.debian.org/debian-lts-announce/2024/03/msg00027.html
