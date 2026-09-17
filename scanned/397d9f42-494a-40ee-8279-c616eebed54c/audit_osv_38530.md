# [C] SAIL has heap buffer overflow in TGA RLE decoder — raw packet path missing bounds check

## Summary
Severity: Critical
Advisory: CVE-2026-40494
Aliases: GHSA-cp2j-rwh4-r46f
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-40494
Type: osv

## Details
SAIL is a cross-platform library for loading and saving images with support for animation, metadata, and ICC profiles. Prior to commit 45d48d1f2e8e0d73e80bc1fd5310cb57f4547302, the TGA codec's RLE decoder in `tga.c` has an asymmetric bounds check vulnerability. The run-packet path (line 297) correctly clamps the repeat count to the remaining buffer space, but the raw-packet path (line 305-311) has no equivalent bounds check. This allows writing up to 496 bytes of attacker-controlled data past the end of a heap buffer. Commit 45d48d1f2e8e0d73e80bc1fd5310cb57f4547302 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40494.json
- https://github.com/HappySeaFox/sail/security/advisories/GHSA-cp2j-rwh4-r46f
- https://nvd.nist.gov/vuln/detail/CVE-2026-40494
- https://github.com/HappySeaFox/sail/commit/45d48d1f2e8e0d73e80bc1fd5310cb57f4547302
