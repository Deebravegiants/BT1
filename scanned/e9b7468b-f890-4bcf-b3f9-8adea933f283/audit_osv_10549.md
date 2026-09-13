# [M] CVE-2017-16946

## Summary
Severity: Medium
Advisory: CVE-2017-16946
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-25
Source: https://osv.dev/vulnerability/CVE-2017-16946
Type: osv

## Details
The admin_edit function in app/Controller/UsersController.php in MISP 2.4.82 mishandles the enable_password field, which allows admins to discover a hashed password by reading the audit log.

## References
- https://github.com/MISP/MISP/commit/7d5890b2fc63285f010d5845913894dd71cf232c
