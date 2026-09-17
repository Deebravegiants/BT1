# [H] CVE-2020-19858

## Summary
Severity: High
Advisory: CVE-2020-19858
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2020-19858
Type: osv

## Details
Platinum Upnp SDK through 1.2.0 has a directory traversal vulnerability. The attack could remote attack victim by sending http://ip:port/../privacy.avi URL to compromise a victim's privacy.

## References
- https://github.com/plutinosoft/Platinum/issues/22
- https://github.com/plutinosoft/Platinum/commit/9a4ceaccb1585ec35c45fd8e2585538fff6a865e
