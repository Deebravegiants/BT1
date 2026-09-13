# [H] CVE-2021-40574

## Summary
Severity: High
Advisory: CVE-2021-40574
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40574
Type: osv

## Details
The binary MP4Box in Gpac from 0.9.0-preview to 1.0.1 has a double-free vulnerability in the gf_text_get_utf8_line function in load_text.c, which allows attackers to cause a denial of service, even code execution and escalation of privileges.

## References
- https://github.com/gpac/gpac/blob/v0.9.0-preview/src/filters/load_text.c#L232
- https://github.com/gpac/gpac/blob/v0.9.0-preview/src/filters/load_text.c#L304
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1897
- https://github.com/gpac/gpac/commit/30ac5e5236b790accd1f25347eebf2dc8c6c1bcb
