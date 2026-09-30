# [M] CVE-2018-1000870

## Summary
Severity: Medium
Advisory: CVE-2018-1000870
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000870
Type: osv

## Details
PHPipam version 1.3.2 and earlier contains a CWE-79 vulnerability in /app/admin/users/print-user.php that can result in Execute code in the victims browser. This attack appear to be exploitable via Attacker change theme parameter in user settings. Admin(Victim) views user in admin-panel and gets exploited.. This vulnerability appears to have been fixed in 1.4.

## References
- https://github.com/phpipam/phpipam/commit/552fbb0fc7ecb84bda4a131b4f290a3de9980040
- https://github.com/phpipam/phpipam/issues/2326
