# [C] CVE-2019-14462

## Summary
Severity: Critical
Advisory: CVE-2019-14462
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-14462
Type: osv

## Details
An issue was discovered in libmodbus before 3.0.7 and 3.1.x before 3.1.5. There is an out-of-bounds read for the MODBUS_FC_WRITE_MULTIPLE_COILS case, aka VD-1302.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HAGHQFJTJCMYHW553OUWJ3YIJR6PJHB7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PRAQZXGAZY6UGWZ6CD33QEFLL7AWW233/
- https://libmodbus.org/2019/stable-and-development-releases/
- https://lists.debian.org/debian-lts-announce/2021/11/msg00020.html
- https://github.com/stephane/libmodbus/commit/5ccdf5ef79d742640355d1132fa9e2abc7fbaefc
