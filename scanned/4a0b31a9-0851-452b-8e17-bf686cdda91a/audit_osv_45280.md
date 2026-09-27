# [M] A vulnerability was found in the libtiff library

## Summary
Severity: Medium
Advisory: JLSEC-2025-302
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-302
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
A vulnerability was found in the libtiff library. This flaw causes a heap buffer overflow issue via the `TIFFTAG_INKNAMES` and `TIFFTAG_NUMBEROFINKS` values.

## References
- http://seclists.org/fulldisclosure/2023/Oct/24
- https://access.redhat.com/security/cve/CVE-2023-30774
- https://bugzilla.redhat.com/show_bug.cgi?id=2187139
- https://gitlab.com/libtiff/libtiff/-/issues/463
- https://security.netapp.com/advisory/ntap-20230703-0002/
- https://support.apple.com/kb/HT213984
