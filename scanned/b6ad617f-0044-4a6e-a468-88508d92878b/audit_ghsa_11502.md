# [H] Improper handling of null Unicode character when parsing JSON in github.com/modelcontextprotocol/go-sdk

## Summary
Severity: High
Advisory: GHSA-q382-vc8q-7jhj
CWE: CWE-1395, CWE-436
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-q382-vc8q-7jhj
Type: github-advisory

## Affected
- Go: `github.com/modelcontextprotocol/go-sdk` — affected >=0 <1.4.1

## Details
The Go SDK recently transitioned to the `segmentio/encoding` library for JSON parsing in version 1.3.1. While this change addressed both case-insensitivity and ASCII folding issues, the new parser implemented aggressive key matching that treated keys with `null` Unicode characters appended at the end as equivalent to their base strings.

#### Impact

When combined with duplicate keys, the described behavior leads to a "last key wins" resolution that could override the intended MCP message. This had the potential for:
  - **Bypassing intermediary inspection:** Proxies or policy layers that matched on exact field names may have failed to detect or filter these messages.
  - **Cross-implementation inconsistency:** Other MCP SDKs (TypeScript, Python) use case-sensitive parsing and would reject the same messages, creating potential security-boundary confusion.

####  Fix:

The `segmentio/encoding` package was patched with a fix in https://github.com/segmentio/encoding/commit/7d5a25dbc5da13aed3cb047a127e4d0e96f536fb and a new version of the package was released (`v0.5.4`). The SDK switched to the patched version of the dependency in 724dd47aa. Users are advised to update to v1.4.1 to resolve this issue.

#### Credits:
Thank you to Francesco Lacerenza (Doyensec) for reporting this issue.

## References
- https://github.com/modelcontextprotocol/go-sdk/security/advisories/GHSA-q382-vc8q-7jhj
- https://github.com/modelcontextprotocol/go-sdk/commit/724dd47aa3431b9d4cf9ac2eebbf7b38a629afca
- https://github.com/segmentio/encoding/commit/7d5a25dbc5da13aed3cb047a127e4d0e96f536fb
- https://github.com/modelcontextprotocol/go-sdk
