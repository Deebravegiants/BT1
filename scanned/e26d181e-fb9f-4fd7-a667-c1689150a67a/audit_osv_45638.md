# [H] In libexif through 0.6.25, an integer underflow in size checking for Fuji and Olympus MakerNote...

## Summary
Severity: High
Advisory: JLSEC-2026-152
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-152
Type: osv

## Affected
- Julia: `libexif_jll` — affected >=0 <0.6.26+0

## Details
In libexif through 0.6.25, an integer underflow in size checking for Fuji and Olympus MakerNote decoding could be used by attackers to crash or leak information out of libexif-using programs.

## References
- https://github.com/advisories/GHSA-p6wp-hhx9-7jj5
- https://github.com/libexif/libexif/commit/dc6eac6e9655d14d0779d99e82d0f5f442d2f34b
- https://nvd.nist.gov/vuln/detail/CVE-2026-40386
