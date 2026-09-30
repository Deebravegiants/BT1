# [M] Fastify's Missing End Anchor in "subtypeNameReg" Allows Malformed Content-Types to Pass Validation

## Summary
Severity: Medium
Advisory: GHSA-573f-x89g-hqp9
CVE: CVE-2026-3419
CWE: CWE-185
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-573f-x89g-hqp9
Type: github-advisory

## Affected
- npm: `fastify` — affected >=5.7.2 <5.8.1

## Details
# Description

Fastify incorrectly accepts malformed `Content-Type` headers containing trailing characters after the subtype token, in violation of [RFC 9110 §8.3.1](https://httpwg.org/specs/rfc9110.html#field.content-type). For example, a request sent with `Content-Type: application/json garbage` passes validation and is processed normally, rather than being rejected with `415 Unsupported Media Type`.

When regex-based content-type parsers are in use (a documented Fastify feature), the malformed value is matched against registered parsers using the full string including the trailing garbage. This means a request with an invalid content-type may be routed to and processed by a parser it should never have reached.

## Impact

An attacker can send requests with RFC-invalid `Content-Type` headers that bypass validity checks, reach content-type parser matching, and be processed by the server. Requests that should be rejected at the validation stage are instead handled as if the content-type were valid.

## Workarounds

Deploy a WAF rule to protect against this

## Fix

The fix is available starting with v5.8.1.

## References
- https://github.com/fastify/fastify/security/advisories/GHSA-573f-x89g-hqp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-3419
- https://github.com/fastify/fastify/commit/67f6c9b32cb3623d3c9470cc17ed830dd2f083d7
- https://cna.openjsf.org/security-advisories.html
- https://github.com/advisories/GHSA-573f-x89g-hqp9
- https://github.com/fastify/fastify
- https://httpwg.org/specs/rfc9110.html#field.content-type
- https://www.cve.org/CVERecord?id=CVE-2026-3419
