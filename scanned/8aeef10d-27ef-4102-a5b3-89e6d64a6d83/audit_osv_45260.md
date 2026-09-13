# [M] libtiff's tiffcrop utility has a `uint32_t` underflow that can lead to out of bounds read and write....

## Summary
Severity: Medium
Advisory: JLSEC-2025-276
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-276
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.4.0+0

## Details
libtiff's tiffcrop utility has a `uint32_t` underflow that can lead to out of bounds read and write. An attacker who supplies a crafted file to tiffcrop (likely via tricking a user to run tiffcrop on it with certain parameters) could cause a crash or in some cases, further exploitation.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2118847
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
- https://www.debian.org/security/2023/dsa-5333
