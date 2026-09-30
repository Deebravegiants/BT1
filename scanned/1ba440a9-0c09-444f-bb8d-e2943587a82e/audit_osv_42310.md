# [M] Sonic 3 A.I.R. Unbounded Memory Allocation DoS via ReceivedPacketCache

## Summary
Severity: Medium
Advisory: CVE-2026-66733
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-66733
Type: osv

## Details
Sonic 3 A.I.R. before commit 2492d18 contains an unbounded memory allocation vulnerability in ReceivedPacketCache::enqueuePacket() that allows unauthenticated remote attackers to crash the server process by sending a crafted UDP packet with mUniquePacketID set to the maximum uint32 value. The mUniquePacketID field is read directly from the UDP wire-format packet header without bounds checking, causing the server to allocate one CacheItem per missing packet ID gap, exhausting available host memory and propagating an uncaught std::bad_alloc exception to std::terminate().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66733.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66733
- https://www.vulncheck.com/advisories/sonic-3-a-i-r-unbounded-memory-allocation-dos-via-receivedpacketcache
- https://github.com/Eukaryot/sonic3air/commit/2492d1882cd2cf1cc1d7415729ce5c4fd686cd4f
- https://github.com/Eukaryot/sonic3air
