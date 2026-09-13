# [M] JLSEC-2026-842

## Summary
Severity: Medium
Advisory: JLSEC-2026-842
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-842
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
The PALM image coder at `coders/palm.c` makes an improper call to AcquireQuantumMemory() in routine WritePALMImage() because it needs to be offset by 256. This can cause a out-of-bounds read later on in the routine. The patch adds 256 to `bytes_per_row` in the call to AcquireQuantumMemory(). This could cause impact to reliability. This flaw affects ImageMagick versions prior to 7.0.8-68.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1891606
- https://bugzilla.redhat.com/show_bug.cgi?id=1891606
- https://lists.debian.org/debian-lts-announce/2021/01/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00010.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
