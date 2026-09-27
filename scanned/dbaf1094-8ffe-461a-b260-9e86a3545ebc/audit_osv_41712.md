# [M] Libevent: `evtag_unmarshal_header()` decodes a wire `uint32` length into a signed `int` return value.

## Summary
Severity: Medium
Advisory: CVE-2026-63384
Aliases: GHSA-45c6-qx49-89m8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63384
Type: osv

## Details
Libevent is an event notification library. Prior to 2.1.13 and 2.2.2-alpha, libevent has an incorrect integer conversion in event_tagging.c when evtag_unmarshal_header uses evtag_decode_int to decode an attacker-controlled uint32 payload length and returns it as a signed int. Values above INT_MAX become negative or truncated, and evtag_unmarshal_string can use the converted value in allocation sizing, producing a wrapped large allocation request and denial of service. This issue is fixed in versions 2.1.13 and 2.2.2-alpha.

## References
- https://github.com/libevent/libevent/releases/tag/release-2.1.13-stable
- https://github.com/libevent/libevent/releases/tag/release-2.2.2-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63384.json
- https://github.com/libevent/libevent/security/advisories/GHSA-45c6-qx49-89m8
- https://nvd.nist.gov/vuln/detail/CVE-2026-63384
- https://github.com/libevent/libevent/commit/109c16499282959d70f56ec3baf4c8b1e6646bda
- https://github.com/libevent/libevent/commit/5e3c6ebe342b34c5a9bcf48e9a32ad6708b9c416
