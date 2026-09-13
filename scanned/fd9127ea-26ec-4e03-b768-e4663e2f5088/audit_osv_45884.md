# [H] JLSEC-2026-440

## Summary
Severity: High
Advisory: JLSEC-2026-440
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-440
Type: osv

## Affected
- Julia: `libwebp_jll` — affected >=0 <1.3.2+0

## Details
There exists a use after free/double free in libwebp. An attacker can use the ApplyFiltersAndEncode() function and loop through to free best.bw and assign best = trial pointer. The second loop will then return 0 because of an Out of memory error in VP8 encoder, the pointer is still assigned to trial and the AddressSanitizer will attempt a double free.

## References
- https://chromium.googlesource.com/webm/libwebp
- https://security.gentoo.org/glsa/202309-05
