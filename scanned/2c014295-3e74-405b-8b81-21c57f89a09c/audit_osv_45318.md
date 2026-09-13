# [H] An issue was discovered in libxml2 before 2.10.3

## Summary
Severity: High
Advisory: JLSEC-2025-77
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-77
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.10.3+0

## Details
An issue was discovered in libxml2 before 2.10.3. When parsing a multi-gigabyte XML document with the `XML_PARSE_HUGE` parser option enabled, several integer counters can overflow. This results in an attempt to access an array at a negative 2GB offset, typically leading to a segmentation fault.

## References
- http://seclists.org/fulldisclosure/2022/Dec/21
- http://seclists.org/fulldisclosure/2022/Dec/24
- http://seclists.org/fulldisclosure/2022/Dec/25
- http://seclists.org/fulldisclosure/2022/Dec/26
- http://seclists.org/fulldisclosure/2022/Dec/27
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/c846986356fc149915a74972bf198abc266bc2c0
- https://gitlab.gnome.org/GNOME/libxml2/-/tags/v2.10.3
- https://security.netapp.com/advisory/ntap-20221209-0003/
- https://support.apple.com/kb/HT213531
- https://support.apple.com/kb/HT213533
- https://support.apple.com/kb/HT213534
- https://support.apple.com/kb/HT213535
- https://support.apple.com/kb/HT213536
