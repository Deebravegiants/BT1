# [H] libsixel: integer overflow in encoder

## Summary
Severity: High
Advisory: CVE-2026-44636
Aliases: GHSA-hx93-w8p2-ffh5
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44636
Type: osv

## Details
libsixel is a SIXEL encoder/decoder implementation derived from kmiya's sixel. From  to 1.8.7-r1, signed integer overflow in sixel_encode_highcolor's allocation size calculation can lead to a heap buffer overflow. The public sixel_encode entry point validates only that width and height are greater than zero, with no upper bound. width and height are multiplied as plain int when computing the allocation size for paletted_pixels and normalized_pixels. Any caller that asks libsixel to encode a pixel buffer with width times height greater than INT_MAX (about 2.15 billion) will hit a wrapped allocation size; under the right wrap, the malloc succeeds with a buffer much smaller than the encoder expects, and the encoder writes past the end of the heap allocation. This vulnerability is fixed in 1.8.7-r2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44636.json
- https://github.com/saitoha/libsixel/security/advisories/GHSA-hx93-w8p2-ffh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44636
