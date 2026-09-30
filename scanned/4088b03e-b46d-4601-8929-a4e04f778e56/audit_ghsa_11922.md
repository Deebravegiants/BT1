# [M] Hono Vulnerable to SSE Control Field Injection via CR/LF in writeSSE()

## Summary
Severity: Medium
Advisory: GHSA-p6xx-57qc-3wxr
CVE: CVE-2026-29085
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-p6xx-57qc-3wxr
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.4

## Details
## Summary

When using `streamSSE()` in Streaming Helper, the `event`, `id`, and `retry` fields were not validated for carriage return (`\r`) or newline (`\n`) characters.

Because the SSE protocol uses line breaks as field delimiters, this could allow injection of additional SSE fields within the same event frame if untrusted input was passed into these fields.

## Details

The SSE helper builds event frames by joining lines with `\n`. While multi-line `data:` fields are handled according to the SSE specification, the `event`, `id`, and `retry` fields previously allowed raw values without rejecting embedded CR/LF characters.

Including CR/LF in these control fields could allow unintended additional fields (such as `data:`, `id:`, or `retry:`) to be injected into the event stream.

The issue has been fixed by rejecting CR/LF characters in these fields.

## Impact

An attacker could manipulate the structure of SSE event frames if an application passed user-controlled input directly into `event`, `id`, or `retry`.

Depending on application behavior, this could result in injected SSE fields or altered event stream handling. Applications that render `e.data` in an unsafe manner (for example, using `innerHTML`) could potentially expose themselves to client-side script injection.

This issue affects applications that rely on the SSE helper to enforce protocol-level constraints.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-p6xx-57qc-3wxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-29085
- https://github.com/honojs/hono/commit/f4123ed9ea3c7c52380cc99a079a4d773838846e
- https://github.com/honojs/hono
