# [H] CVE-2018-6926

## Summary
Severity: High
Advisory: CVE-2018-6926
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-12
Source: https://osv.dev/vulnerability/CVE-2018-6926
Type: osv

## Details
In app/Controller/ServersController.php in MISP 2.4.87, a server setting permitted the override of a path variable on certain Red Hed Enterprise Linux and CentOS systems (where rh_shell_fix was enabled), and consequently allowed site admins to inject arbitrary OS commands. The impact is limited by the setting being only accessible to the site administrator.

## References
- https://github.com/MISP/MISP/commit/0a2aa9d52492d960b9a161160acedbe9caaa4126
