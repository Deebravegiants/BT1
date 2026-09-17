# [M] Libevent: decode_tag_internal() can lead to out-of-bounds read

## Summary
Severity: Medium
Advisory: CVE-2026-63383
Aliases: GHSA-fj29-64w6-73h6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63383
Type: osv

## Details
Libevent is an event notification library. Prior to 2.1.13 and 2.2.2-alpha, libevent can read beyond a contiguous evbuffer region in event_tagging.c when decode_tag_internal requests at most five bytes from evbuffer_pullup but iterates using the full logical buffer length. A fragmented evbuffer containing a six-byte malformed tag can therefore advance past the pullup window and trigger an out-of-bounds read, which can crash a process that decodes attacker-controlled tagged RPC data. This issue is fixed in versions 2.1.13 and 2.2.2-alpha.

## References
- https://github.com/libevent/libevent/releases/tag/release-2.1.13-stable
- https://github.com/libevent/libevent/releases/tag/release-2.2.2-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63383.json
- https://github.com/libevent/libevent/security/advisories/GHSA-fj29-64w6-73h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-63383
- https://github.com/libevent/libevent/commit/91ed8745eebabdd27592a83d350338a8c4626321
- https://github.com/libevent/libevent/commit/e1f9e21887c6b104e206a718385ba3ffc75180cb
