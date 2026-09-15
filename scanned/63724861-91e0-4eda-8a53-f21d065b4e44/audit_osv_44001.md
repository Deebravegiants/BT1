# [H] libp2p: Circuit relay v2 server reservation refresh leaks abort listeners and allows remote resource exhaustion

## Summary
Severity: High
Advisory: CVE-2026-77384
Aliases: GHSA-x787-gh7p-hmq7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-77384
Type: osv

## Details
libp2p is a JavaScript implementation of the libp2p networking stack. Prior to version 4.2.9, the reservation refresh path in reservation-store.ts reuses the same retimeableSignal but unconditionally registers another abort listener on every refresh. As a result, a remote peer can repeatedly send valid RESERVE requests for the same reservation, causing unbounded listener and closure growth in @libp2p/circuit-relay-v2 relay servers and leading to denial of service. This issue is fixed in version 4.2.9.

## References
- https://github.com/libp2p/js-libp2p/releases/tag/circuit-relay-v2-v4.2.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77384.json
- https://github.com/libp2p/js-libp2p/security/advisories/GHSA-x787-gh7p-hmq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-77384
- https://github.com/libp2p/js-libp2p/commit/4bb8fbe8d3f3590e4af51a1f5f7de56fffa5804d
