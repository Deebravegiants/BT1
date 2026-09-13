# [M] CVE-2026-23922

## Summary
Severity: Medium
Advisory: CVE-2026-23922
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-23922
Type: osv

## Details
The email media OAuth field 'Client secret' cannot be read after saving, but a Super Admin can leak it by setting a malicious 'Token endpoint'. Changes were made to reset the client secret upon changing the token endpoint.

## References
- https://support.zabbix.com/browse/ZBX-28067
