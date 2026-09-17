# [M] CVE-2025-49643

## Summary
Severity: Medium
Advisory: CVE-2025-49643
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-01
Source: https://osv.dev/vulnerability/CVE-2025-49643
Type: osv

## Details
An authenticated Zabbix user (including Guest) is able to cause disproportionate CPU load on the webserver by sending specially crafted parameters to /imgstore.php, leading to potential denial of service.

## References
- https://support.zabbix.com/browse/ZBX-27284
