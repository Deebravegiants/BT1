# [M] CVE-2018-6883

## Summary
Severity: Medium
Advisory: CVE-2018-6883
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-24
Source: https://osv.dev/vulnerability/CVE-2018-6883
Type: osv

## Details
Piwigo before 2.9.3 has SQL injection in admin/tags.php in the administration panel, via the tags array parameter in an admin.php?page=tags request. The attacker must be an administrator.

## References
- https://github.com/Piwigo/Piwigo/issues/839
- https://pastebin.com/tPebQFy4
