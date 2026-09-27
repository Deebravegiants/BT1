# [H] cowlib: Decompression Bomb in cow_spdy:inflate/2 Allows Memory Exhaustion via Crafted SPDY Frame

## Summary
Severity: High
Advisory: GHSA-84f2-rp86-235p
CVE: CVE-2026-43970
CWE: CWE-409
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-84f2-rp86-235p
Type: github-advisory

## Affected
- Hex: `cowlib` — affected >=0.1.0 <2.16.1

## Details
Improper Handling of Highly Compressed Data (Data Amplification) vulnerability in ninenines cowlib allows unauthenticated remote denial of service via memory exhaustion.

cow_spdy:inflate/2 in cowlib passes peer-supplied compressed bytes directly to zlib:inflate/2 with no output size bound. The SPDY header compression dictionary (?ZDICT) is public, and zlib compresses long runs of repeated bytes at roughly 1024:1, so a few kilobytes of SPDY frame payload can decompress to gigabytes on the BEAM heap, OOM-killing the node. A single unauthenticated SPDY frame is sufficient to trigger the condition. The parsers for syn_stream, syn_reply, and headers frame types are all affected via cow_spdy:parse_headers/2.

This issue affects cowlib from 0.1.0 before 2.16.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43970
- https://github.com/ninenines/cowlib/commit/16aad3fb9f81f5cda4d1706ff0c54237c619c282
- https://cna.erlef.org/cves/CVE-2026-43970.html
- https://github.com/ninenines/cowlib
- https://osv.dev/vulnerability/EEF-CVE-2026-43970
