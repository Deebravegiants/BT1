# [H] CVE-2017-7529

## Summary
Severity: High
Advisory: CVE-2017-7529
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-13
Source: https://osv.dev/vulnerability/CVE-2017-7529
Type: osv

## Details
Nginx versions since 0.5.6 up to and including 1.13.2 are vulnerable to integer overflow vulnerability in nginx range filter module resulting into leak of potentially sensitive information triggered by specially crafted request.

## References
- http://mailman.nginx.org/pipermail/nginx-announce/2017/000200.html
- http://seclists.org/fulldisclosure/2021/Sep/36
- http://www.securityfocus.com/bid/99534
- http://www.securitytracker.com/id/1039238
- https://access.redhat.com/errata/RHSA-2017:2538
- https://puppet.com/security/cve/cve-2017-7529
- https://support.apple.com/kb/HT212818
