# [H] ALPINE-CVE-2026-33164

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-33164
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33164
Type: osv

## Affected
- Alpine:v3.24: `libde265` — affected >=0 <1.0.18-r0

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.0.17, a malformed H.265 PPS NAL unit causes a segmentation fault in pic_parameter_set::set_derived_values(). This issue has been patched in version 1.0.17.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33164
