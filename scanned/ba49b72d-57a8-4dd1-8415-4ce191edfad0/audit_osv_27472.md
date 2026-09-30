# [C] CVE-2024-22122

## Summary
Severity: Critical
Advisory: CVE-2024-22122
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-22122
Type: osv

## Details
Zabbix allows to configure SMS notifications. AT command injection occurs on "Zabbix Server" because there is no validation of "Number" field on Web nor on Zabbix server side. Attacker can run test of SMS providing specially crafted phone number and execute additional AT commands on modem.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00000.html
- https://support.zabbix.com/browse/ZBX-25012
