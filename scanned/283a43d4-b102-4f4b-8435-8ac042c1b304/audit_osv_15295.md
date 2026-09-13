# [H] CVE-2019-15075

## Summary
Severity: High
Advisory: CVE-2019-15075
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-20
Source: https://osv.dev/vulnerability/CVE-2019-15075
Type: osv

## Details
An issue was discovered in iNextrix ASTPP before 4.0.1. web_interface/astpp/application/config/config.php does not have strong random keys, as demonstrated by use of the 8YSDaBtDHAB3EQkxPAyTz2I5DttzA9uR private key and the r)fddEw232f encryption key.

## References
- https://github.com/iNextrix/ASTPP/commit/9877ec62556f0470030acd306b24bc94fdcbe2ae
