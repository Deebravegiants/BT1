# [M] CVE-2021-30144

## Summary
Severity: Medium
Advisory: CVE-2021-30144
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-04-06
Source: https://osv.dev/vulnerability/CVE-2021-30144
Type: osv

## Details
The Dashboard plugin through 1.0.2 for GLPI allows remote low-privileged users to bypass access control on viewing information about the last ten events, the connected users, and the users in the tech category. For example, plugins/dashboard/front/main2.php can be used.

## References
- https://github.com/Kitsun3Sec/exploits/tree/master/cms/GLPI/dashboard-plugin
- https://plugins.glpi-project.org/#/plugin/dashboard
