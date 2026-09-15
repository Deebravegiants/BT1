# [H] Sereal::Decoder versions before 5.005 for Perl allow heap out-of-bounds read via crafted input

## Summary
Severity: High
Advisory: CVE-2026-8796
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-05-31
Source: https://osv.dev/vulnerability/CVE-2026-8796
Type: osv

## Details
Sereal::Decoder versions before 5.005 for Perl allow heap out-of-bounds read via crafted input.

In Perl/Decoder/srl_decoder.c, srl_read_object() and srl_read_hash() process a COPY tag, a back-reference whose target byte the decoder re-decodes as a fresh tag. When that target byte matches the SHORT_BINARY pattern (an inline string whose length is encoded in the low bits of the tag), the resulting read is not bounded to precede the COPY tag's own offset and can run past the end of the input buffer. An attacker controlled COPY offset can land inside a previously decoded value rather than on a tag boundary, planting a byte that the decoder reads as a SHORT_BINARY tag and consuming up to 31 following bytes from the heap as a class name (OBJECT path) or hash key (HASH path).

## References
- http://www.openwall.com/lists/oss-security/2026/06/01/1
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8796.json
- https://metacpan.org/release/YVES/Sereal-Decoder-5.005/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-8796
- https://github.com/Sereal/Sereal/commit/303a2c69cdba80bf37a3ff43461e0aa78198a7a3.patch
- https://github.com/Sereal/Sereal
