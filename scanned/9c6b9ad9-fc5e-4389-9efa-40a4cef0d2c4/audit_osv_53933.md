# [H] CVE-2023-32725

## Summary
Severity: High
Advisory: CVE-2023-32725
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/CVE-2023-32725
Type: osv

## Details
The website configured in the URL widget will receive a session cookie when testing or executing scheduled reports. The received session cookie can then be used to access the frontend as the particular user.

## References
- https://support.zabbix.com/browse/ZBX-23854
