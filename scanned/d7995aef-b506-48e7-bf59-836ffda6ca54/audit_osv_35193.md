# [H] Traccar Missing Origin Validation in WebSockets

## Summary
Severity: High
Advisory: CVE-2025-68930
Aliases: GHSA-69x6-wcx2-vghp
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/CVE-2025-68930
Type: osv

## Details
Versions of the Traccar open-source GPS tracking system up to and including 6.11.1 contain a Cross-Site WebSocket Hijacking (CSWSH) vulnerability in the `/api/socket` endpoint. The application fails to validate the `Origin` header during the WebSocket handshake. This allows a remote attacker to bypass the Same Origin Policy (SOP) and establish a full-duplex WebSocket connection using a legitimate user's credentials (JSESSIONID). As of time of publication, it is unclear whether a fix is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68930.json
- https://github.com/traccar/traccar/security/advisories/GHSA-69x6-wcx2-vghp
- https://nvd.nist.gov/vuln/detail/CVE-2025-68930
