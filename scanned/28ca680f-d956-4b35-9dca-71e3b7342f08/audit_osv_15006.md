# [C] CVE-2019-12951

## Summary
Severity: Critical
Advisory: CVE-2019-12951
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-24
Source: https://osv.dev/vulnerability/CVE-2019-12951
Type: osv

## Details
An issue was discovered in Mongoose before 6.15. The parse_mqtt() function in mg_mqtt.c has a critical heap-based buffer overflow.

## References
- https://github.com/cesanta/mongoose/releases/tag/6.15
- https://github.com/cesanta/mongoose/commit/b3e0f780c34cea88f057a62213c012aa88fe2deb
