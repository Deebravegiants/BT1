# [H] CVE-2018-16608

## Summary
Severity: High
Advisory: CVE-2018-16608
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/CVE-2018-16608
Type: osv

## Details
In Monstra CMS 3.0.4, an attacker with 'Editor' privileges can change the password of the administrator via an admin/index.php?id=users&action=edit&user_id=1, Insecure Direct Object Reference (IDOR).

## References
- https://github.com/monstra-cms/monstra/issues/453
