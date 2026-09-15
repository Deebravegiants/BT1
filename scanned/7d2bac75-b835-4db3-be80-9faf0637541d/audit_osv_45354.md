# [M] ImageMagick before 7.1.2-15 contains a use-after-free vulnerability in the PDB decoder that uses...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1054
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1054
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-15 contains a use-after-free vulnerability in the PDB decoder that uses a stale pointer when memory allocation fails. Attackers can trigger this vulnerability by processing malicious PDB files to cause crashes or write a single zero byte to freed memory.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-3j4x-rwrx-xxj9
- https://github.com/advisories/GHSA-j6f7-9c5w-9r2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-56373
- https://www.vulncheck.com/advisories/imagemagick-use-after-free-write-in-pdb-decoder
