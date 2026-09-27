# [H] BACnet Stack WriteProperty decoding length underflow leads to OOB read and crash

## Summary
Severity: High
Advisory: CVE-2026-26264
Aliases: GHSA-phjh-v45p-gmjj
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-26264
Type: osv

## Details
BACnet Stack is a BACnet open source protocol stack C library for embedded systems. Prior to 1.5.0rc4 and 1.4.3rc2, a malformed WriteProperty request can trigger a length underflow in the BACnet stack, leading to an out‑of‑bounds read and a crash (DoS). The issue is in wp.c within wp_decode_service_request. When decoding the optional priority context tag, the code passes apdu_len - apdu_size to bacnet_unsigned_context_decode without validating that apdu_size <= apdu_len. If a truncated APDU reaches this path, apdu_len - apdu_size underflows, resulting in a large size being used for decoding and an out‑of‑bounds read. This vulnerability is fixed in 1.5.0rc4 and 1.4.3rc2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26264.json
- https://github.com/bacnet-stack/bacnet-stack/security/advisories/GHSA-phjh-v45p-gmjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-26264
- https://github.com/bacnet-stack/bacnet-stack/commit/4cc8067c86f26e2b08b2c8f4d27f8e07de4d4708
