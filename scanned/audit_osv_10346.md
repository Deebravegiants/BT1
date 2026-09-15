# [M] CVE-2017-15052

## Summary
Severity: Medium
Advisory: CVE-2017-15052
Aliases: GHSA-5qr3-4839-88gf
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-11-27
Source: https://osv.dev/vulnerability/CVE-2017-15052
Type: osv

## Details
TeamPass before 2.1.27.9 does not properly enforce manager access control when requesting users.queries.php. It is then possible for a manager user to delete an arbitrary user (including admin), or modify attributes of any arbitrary user except administrator. To exploit the vulnerability, an authenticated attacker must have the manager rights on the application, then tamper with the requests sent directly, for example by changing the "id" parameter when invoking "delete_user" on users.queries.php.

## References
- https://github.com/nilsteampassnet/TeamPass/commit/8f2d51dd6c24f76e4f259d0df22cff9b275f2dd1
- http://blog.amossys.fr/teampass-multiple-cve-01.html
