# [H] Protocol::HTTP2 versions before 1.13 for Perl is vulnerable to a HTTP/2 Bomb

## Summary
Severity: High
Advisory: CVE-2026-10725
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-06
Source: https://osv.dev/vulnerability/CVE-2026-10725
Type: osv

## Details
Protocol::HTTP2 versions before 1.13 for Perl is vulnerable to a HTTP/2 Bomb.

Protocol::HTTP2's inbound HPACK path has no header-list size limit, so a small HTTP/2 request can expand into large server memory (the "HTTP/2 bomb").

The headers_decode method materialises a full key+value copy per indexed reference with no running size check, and the stream_header_block_add method appends (since version 1.12) every CONTINUATION frame to the per-stream buffer unbounded.

MAX_HEADER_LIST_SIZE (default 65536) is advertised in SETTINGS but never consulted on decode.  It is absent from the decoder and from the :limits export tag.

## References
- http://www.openwall.com/lists/oss-security/2026/06/06/7
- https://cpan.org/modules
- https://metacpan.org/release/CRUX/Protocol-HTTP2-1.12/source/lib/Protocol/HTTP2/HeaderCompression.pm#L133
- https://metacpan.org/release/CRUX/Protocol-HTTP2-1.12/source/lib/Protocol/HTTP2/Stream.pm#L414
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10725.json
- https://metacpan.org/release/CRUX/Protocol-HTTP2-1.13/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-10725
- https://github.com/vlet/p5-Protocol-HTTP2/commit/822bf22224adbd662e8d0b865eeacb2b294d16cd.patch
- https://security.metacpan.org/patches/P/Protocol-HTTP2/1.12/CVE-2026-10725-r2.patch
- https://github.com/vlet/p5-Protocol-HTTP2
