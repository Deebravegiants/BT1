# [H] In libexif through 0.6.25, an unsigned 32bit integer overflow in Nikon MakerNote handling could be...

## Summary
Severity: High
Advisory: JLSEC-2026-151
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-151
Type: osv

## Affected
- Julia: `libexif_jll` — affected >=0 <0.6.26+0

## Details
In libexif through 0.6.25, an unsigned 32bit integer overflow in Nikon MakerNote handling could be used by local attackers to cause crashes or information leaks. This only affects 32bit systems.

## References
- https://github.com/advisories/GHSA-j9xr-5c85-xjhm
- https://github.com/libexif/libexif/commit/93003b93e50b3d259bd2227d8775b73a53c35d58
- https://nvd.nist.gov/vuln/detail/CVE-2026-40385
