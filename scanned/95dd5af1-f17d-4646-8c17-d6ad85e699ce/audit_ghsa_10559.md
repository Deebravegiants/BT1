# [M] @nestjs/core Improperly Neutralizes Special Elements in Output Used by a Downstream Component ('Injection')

## Summary
Severity: Medium
Advisory: GHSA-36xv-jgw5-4q75
CVE: CVE-2026-35515
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-36xv-jgw5-4q75
Type: github-advisory

## Affected
- npm: `@nestjs/core` — affected >=0 <11.1.18

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

[`SseStream._transform()`](https://github.com/nestjs/nest/blob/dea5279ef8fcb568de158003e4281759a2cd7675/packages/core/router/sse-stream.ts) interpolates `message.type` and `message.id` directly into Server-Sent Events text protocol output without sanitizing newline characters (`\r`, `\n`). Since the SSE protocol treats both `\r` and `\n` as field delimiters and `\n\n` as event boundaries, an attacker who can influence these fields through upstream data sources can inject arbitrary SSE events, spoof event types, and corrupt reconnection state. Spring Framework's own security patch ([6e97587](https://github.com/spring-projects/spring-framework/commit/6e9758700a4946be1dca85ca937ef2603e291301)) validates these same fields (`id`, `event`) for the same reason.

Actual impact:

- **Event spoofing**: Attacker forges SSE events with arbitrary `event:` types, causing client-side `EventSource.addEventListener()` callbacks to fire for wrong event types.
- **Data injection**: Attacker injects arbitrary `data:` payloads, potentially triggering XSS if the client renders SSE data as HTML without sanitization.
- **Reconnection corruption**: Attacker injects `id:` fields, corrupting the `Last-Event-ID` header on reconnection, causing the client to miss or replay events.
- **Attack precondition**: Requires the developer to map user-influenced data to the `type` or `id` fields of SSE messages. Direct HTTP request input does not reach these fields without developer code bridging the gap.
-
### Patches
_Has the problem been patched? What versions should users upgrade to?_

Patched in `@nestjs/core@11.1.18`

## References
- https://github.com/nestjs/nest/security/advisories/GHSA-36xv-jgw5-4q75
- https://nvd.nist.gov/vuln/detail/CVE-2026-35515
- https://github.com/nestjs/nest/pull/16686
- https://github.com/nestjs/nest/commit/83558ae774a990a7916141d3abe0b6548ff3a8b2
- https://github.com/nestjs/nest
- https://github.com/nestjs/nest/releases/tag/v11.1.18
