# [C] CVE-2020-22669

## Summary
Severity: Critical
Advisory: CVE-2020-22669
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-02
Source: https://osv.dev/vulnerability/CVE-2020-22669
Type: osv

## Details
Modsecurity owasp-modsecurity-crs 3.2.0 (Paranoia level at PL1) has a SQL injection bypass vulnerability. Attackers can use the comment characters and variable assignments in the SQL syntax to bypass Modsecurity WAF protection and implement SQL injection attacks on Web applications.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00004.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00033.html
- https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/1727
- https://github.com/coreruleset/coreruleset/pull/1793
