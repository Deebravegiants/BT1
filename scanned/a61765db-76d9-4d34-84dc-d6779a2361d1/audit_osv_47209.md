# [H] CVE-2016-10730

## Summary
Severity: High
Advisory: CVE-2016-10730
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-24
Source: https://osv.dev/vulnerability/CVE-2016-10730
Type: osv

## Details
An issue was discovered in Amanda 3.3.1. A user with backup privileges can trivially compromise a client installation. Amstar is an Amanda Application API script. It should not be run by users directly. It uses star to backup and restore data. It runs binaries with root permissions when parsing the command line argument --star-path.

## References
- https://www.exploit-db.com/exploits/39244/
