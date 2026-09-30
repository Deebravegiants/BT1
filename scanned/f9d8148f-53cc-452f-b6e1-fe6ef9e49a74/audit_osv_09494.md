# [M] CVE-2017-0886

## Summary
Severity: Medium
Advisory: CVE-2017-0886
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2017-0886
Type: osv

## Details
Nextcloud Server before 9.0.55 and 10.0.2 suffers from a Denial of Service attack. Due to an error in the application logic an authenticated adversary may trigger an endless recursion in the application leading to a potential Denial of Service.

## References
- https://hackerone.com/reports/174524
- https://nextcloud.com/security/advisory/?id=nc-sa-2017-004
