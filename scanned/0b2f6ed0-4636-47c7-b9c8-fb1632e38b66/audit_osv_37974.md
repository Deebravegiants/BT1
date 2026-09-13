# [M] Nimiq has Allocation of Resources Without Limits or Throttling in its libp2p request/response

## Summary
Severity: Medium
Advisory: CVE-2026-34062
Aliases: GHSA-gh7r-qh4p-q4fr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-34062
Type: osv

## Details
nimiq-libp2p is a Nimiq network implementation based on libp2p. Prior to version 1.3.0, `MessageCodec::read_request` and `read_response` call `read_to_end()` on inbound substreams, so a remote peer can send only a partial frame and keep the substream open. because `Behaviour::new` also sets `with_max_concurrent_streams(1000)`, the node exposes a much larger stalled-slot budget than the library default. The patch for this vulnerability is formally released as part of v1.3.0. No known workarounds are available.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34062.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-gh7r-qh4p-q4fr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34062
- https://github.com/nimiq/core-rs-albatross/commit/c021a5337b808c73571b44999f9753051bac7508
