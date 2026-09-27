# [H] CVE-2026-23925

## Summary
Severity: High
Advisory: CVE-2026-23925
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-23925
Type: osv

## Details
An authenticated Zabbix user (User role) with template/host write permissions is able to create objects via the configuration.import API. This can lead to confidentiality loss by creating unauthorized hosts. Note that the User role is normally not sufficient to create and edit templates/hosts even with write permissions.

## References
- https://support.zabbix.com/browse/ZBX-27567
