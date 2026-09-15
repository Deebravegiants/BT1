# [M] CVE-2022-46768

## Summary
Severity: Medium
Advisory: CVE-2022-46768
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-15
Source: https://osv.dev/vulnerability/CVE-2022-46768
Type: osv

## Details
Arbitrary file read vulnerability exists in Zabbix Web Service Report Generation, which listens on the port 10053. The service does not have proper validation for URL parameters before reading the files.

## References
- https://support.zabbix.com/browse/ZBX-22087
