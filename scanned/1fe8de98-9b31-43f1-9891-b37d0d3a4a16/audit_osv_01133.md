# [H] ALPINE-CVE-2018-20483

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20483
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20483
Type: osv

## Affected
- Alpine:v3.10: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.11: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.12: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.13: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.14: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.15: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.16: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.17: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.18: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.19: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.20: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.21: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.22: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.23: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.24: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.6: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.7: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.8: `wget` — affected >=0 <1.20.1-r0
- Alpine:v3.9: `wget` — affected >=0 <1.20.1-r0

## Details
set_file_metadata in xattr.c in GNU Wget before 1.20.1 stores a file's origin URL in the user.xdg.origin.url metadata attribute of the extended attributes of the downloaded file, which allows local users to obtain sensitive information (e.g., credentials contained in the URL) by reading this attribute, as demonstrated by getfattr. This also applies to Referer information in the user.xdg.referrer.url metadata attribute. According to 2016-07-22 in the Wget ChangeLog, user.xdg.origin.url was partially based on the behavior of fwrite_xattr in tool_xattr.c in curl.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20483
