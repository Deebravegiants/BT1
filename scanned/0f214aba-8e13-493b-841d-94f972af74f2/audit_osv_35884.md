# [H] Protocol::HTTP2 versions before 1.14 for Perl allow memory exhaustion via closed streams that stream_state never removes from the connection stream table

## Summary
Severity: High
Advisory: CVE-2026-16028
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-16028
Type: osv

## Details
Protocol::HTTP2 versions before 1.14 for Perl allow memory exhaustion via closed streams that stream_state never removes from the connection stream table.

When a stream reaches the CLOSED state, stream_state returns the concurrency slot and clears most of the stream's keys, but the entry itself stays in the connection stream table and nothing in the distribution removes it. Stream identifiers increase monotonically, so a peer can open and close streams on one connection indefinitely, each close leaving a residual entry that is retained for the life of the connection.

SETTINGS_MAX_CONCURRENT_STREAMS does not bound this. That setting caps how many streams are live at once and is enforced, while the growth is made of streams the cap has already released, so it accumulates with concurrency never exceeding one. The client keeps the same table and grows the same way against a hostile server.

Measured against a server built on this module, roughly 920 bytes are retained per closed stream for about 19 bytes on the wire, so 100,000 sequential streams on one connection grow server resident memory by about 88 MiB. The streams are ordinary requests that the application accepts and completes.

## References
- http://www.openwall.com/lists/oss-security/2026/09/07/2
- https://cpan.org/modules
- https://metacpan.org/release/CRUX/Protocol-HTTP2-1.13/source/lib/Protocol/HTTP2/Stream.pm#L113-126
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16028.json
- https://metacpan.org/release/CRUX/Protocol-HTTP2-1.14/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-16028
- https://github.com/vlet/p5-Protocol-HTTP2/commit/27a488a34d74fd16f123e5e6186d4f677faa246f.patch
- https://github.com/vlet/p5-Protocol-HTTP2
