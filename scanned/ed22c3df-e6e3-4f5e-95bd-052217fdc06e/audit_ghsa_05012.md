# [M] cowboy and gun affected by an HTTP Request/Response Splitting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w4f7-4cxr-rv3c
CVE: CVE-2026-43966
CWE: CWE-113
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-w4f7-4cxr-rv3c
Type: github-advisory

## Affected
- Hex: `cowboy` — affected >=0 <2.16.0
- Hex: `gun` — affected >=0 <2.16.0

## Details
Improper Neutralization of CRLF Sequences in HTTP Headers ('HTTP Request/Response Splitting') vulnerability in ninenines cowlib allows HTTP response splitting via non-VCHAR bytes in structured-fields string values.

cow_http_struct_hd:escape_string/2 in cowlib only escapes \ and ", passing all other bytes through verbatim. This creates an encoder/decoder asymmetry: the matching parser accepts only printable ASCII (0x20–0x7E, excluding " and \), but the encoder emits any byte including CR and LF. An application that builds a structured HTTP header via cow_http_struct_hd:item/1 (or a higher-level wrapper such as cow_http_hd:wt_protocol/1) from attacker-controlled input can have \r\n injected into the serialized header value. Once on the wire, the injected CRLF terminates the current header and any following bytes are interpreted as a new header, enabling HTTP response splitting.

This issue affects cowlib from 2.9.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43966
- https://github.com/ninenines/cowlib/pull/163#issuecomment-4952645232
- https://github.com/ninenines/cowlib/pull/166#issuecomment-5067554701
- https://github.com/ninenines/cowboy/commit/f77cb9b5e730e300fffb551db1ba5d1c4ed878ef
- https://github.com/ninenines/gun/commit/4f35609eb37109b106a863fc9ba83d7ee64e3e42
- https://cna.erlef.org/cves/CVE-2026-43966.html
- https://github.com/ninenines/cowlib
- https://osv.dev/vulnerability/EEF-CVE-2026-43966
