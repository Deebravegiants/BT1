# [M] mercurius has Uncaught Exception when using subscriptions

## Summary
Severity: Medium
Advisory: GHSA-cm8h-q92v-xcfc
CVE: CVE-2023-22477
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-cm8h-q92v-xcfc
Type: github-advisory

## Affected
- npm: `mercurius` — affected >=9.0.0 <11.5.0
- npm: `mercurius` — affected >=0 <8.13.2

## Details
### Impact

Any users of Mercurius until version v11.5.0 are subjected to a denial of service attack by sending a malformed packet over WebSocket to `/graphql`.

### Patches

This was patched in https://github.com/mercurius-js/mercurius/pull/940.
The patch was released as v11.5.0 and v8.13.2.

### Workarounds

Disable subscriptions.

### References

Reported publicly as https://github.com/mercurius-js/mercurius/issues/939.
The same problem was solved in https://github.com/fastify/fastify-websocket/pull/228

## References
- https://github.com/mercurius-js/mercurius/security/advisories/GHSA-cm8h-q92v-xcfc
- https://nvd.nist.gov/vuln/detail/CVE-2023-22477
- https://github.com/mercurius-js/mercurius/issues/939
- https://github.com/fastify/fastify-websocket/pull/228
- https://github.com/mercurius-js/mercurius/pull/940
- https://github.com/mercurius-js/mercurius
