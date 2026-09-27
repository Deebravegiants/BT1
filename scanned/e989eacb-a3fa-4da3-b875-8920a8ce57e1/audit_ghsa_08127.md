# [H] MCP Go SDK Vulnerable to Improper Handling of Case Sensitivity

## Summary
Severity: High
Advisory: GHSA-wvj2-96wp-fq3f
CVE: CVE-2026-27896
CWE: CWE-178, CWE-436
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-wvj2-96wp-fq3f
Type: github-advisory

## Affected
- Go: `github.com/modelcontextprotocol/go-sdk` — affected >=0 <1.3.1

## Details
The Go MCP SDK used Go's standard encoding/json.Unmarshal for JSON-RPC and MCP protocol message parsing. Go's standard library performs case-insensitive matching of JSON keys to struct field tags — a field tagged json:"method" would also match "Method", "METHOD", etc. Additionally, Go's standard library folds the Unicode characters ſ (U+017F) and K (U+212A) to their ASCII equivalents s and k, meaning fields like "paramſ" would match "params". This violated the JSON-RPC 2.0 specification, which defines exact field names.

#### Impact:

A malicious MCP peer may have been able to send protocol messages with non-standard field casing (e.g., "Method" instead of "method") that the SDK would silently accept. This had the potential for:
  - **Bypassing intermediary inspection:** Proxies or policy layers that matched on exact field names may have failed to detect or filter these messages.
  - **Cross-implementation inconsistency:** Other MCP SDKs (TypeScript, Python) use case-sensitive parsing and would reject the same messages, creating potential security-boundary confusion.

####  Fix:

Go's standard JSON unmarshaling was replaced with a case-sensitive decoder (github.com/segmentio/encoding) in commit 7b8d81c. Users are advised to update to v1.3.1 to resolve this issue.

#### Credits:
MCP Go SDK thanks Francesco Lacerenza (Doyensec) for reporting this issue.

## References
- https://github.com/modelcontextprotocol/go-sdk/security/advisories/GHSA-wvj2-96wp-fq3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-27896
- https://github.com/modelcontextprotocol/go-sdk/commit/7b8d81c264074404abdf5aa16e2cf0c2d9c64cc0
- https://github.com/modelcontextprotocol/go-sdk
