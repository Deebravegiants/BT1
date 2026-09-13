# [H] libcoap Out-of-Bounds Read in OSCORE CBOR Unwrap Handling

## Summary
Severity: High
Advisory: CVE-2026-29013
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-29013
Type: osv

## Details
libcoap contains out-of-bounds read vulnerabilities in OSCORE Appendix B.2 CBOR unwrap handling where get_byte_inc() in src/oscore/oscore_cbor.c relies solely on assert() for bounds checking, which is removed in release builds compiled with NDEBUG. Attackers can send crafted CoAP requests with malformed OSCORE options or responses during OSCORE negotiation to trigger out-of-bounds reads during CBOR parsing and potentially cause out-of-bounds reads through integer wraparound in allocation size computation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29013.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29013
- https://github.com/obgm/libcoap/commit/b7847c4dbb0dbee7c90b09a673d4cae256f03718
