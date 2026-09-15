# [H] libsixel: integer overflow in parser

## Summary
Severity: High
Advisory: CVE-2026-44637
Aliases: GHSA-9jm7-77gr-qghv
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44637
Type: osv

## Details
libsixel is a SIXEL encoder/decoder implementation derived from kmiya's sixel. From  to 1.8.7-r1, a signed integer overflow in the SIXEL parser's image-buffer doubling loop can lead to an out-of-bounds heap write in sixel_decode_raw_impl. context->pos_x grows by repeat_count on every sixel character with no upper bound check. Once pos_x approaches INT_MAX, the expression "pos_x + repeat_count" used to size the image buffer overflows signed int. Depending on how the overflow wraps, the resize check that should reject oversized buffers can be bypassed, after which a subsequent write computes a large attacker-influenced offset into image->data and writes past the allocation. Reachable from any caller that decodes attacker-supplied SIXEL data, including img2sixel. This vulnerability is fixed in 1.8.7-r2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44637.json
- https://github.com/saitoha/libsixel/security/advisories/GHSA-9jm7-77gr-qghv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44637
