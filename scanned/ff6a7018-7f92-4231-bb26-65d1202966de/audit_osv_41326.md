# [H] fluxTransform shared RequestMessageHolder causes cross-message header leakage under async fluxFunction

## Summary
Severity: High
Advisory: CVE-2026-59324
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59324
Type: osv

## Details
When an IntegrationFlow uses .fluxTransform() with an asynchronous/reordering fluxFunction that emits raw payloads, concurrent requests on the same FluxMessageChannel subscription have their reply headers (replyChannel, errorChannel, correlationId, any propagated security/tenant headers) copied from whichever message was most recently consumed upstream.
Spring Integration 7.1.0
Spring Integration 7.0.0 - 7.0.5
Spring Integration 6.5.0 - 6.5.10
Spring Integration 6.4.0 - 6.4.12
Spring Integration 5.5.21 and earlier

## References
- https://spring.io/security/cve-2026-59324
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59324.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59324
