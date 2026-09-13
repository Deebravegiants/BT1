# [H] Buffer Overflow in centra

## Summary
Severity: High
Advisory: GHSA-v6cj-r88p-92rm
CWE: CWE-119
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-09-30
Source: https://github.com/advisories/GHSA-v6cj-r88p-92rm
Type: github-advisory

## Affected
- npm: `centra` — affected >=0 <2.4.0

## Details
## Denial of Service

### Impact

Affected Centra versions will, when not in stream mode, buffer responses to requests into memory with no size limit. This issue affects anyone requesting content from untrusted sources.

### Patches

Version 2.4.0 resolves the issue by limiting the size of buffered response body.

### Workarounds

Attempting workarounds isn't recommended. Updating is preferred.

### For more information

If you have any questions or comments about this advisory, open an issue in [ethanent/centra](https://github.com/ethanent/centra).

## References
- https://github.com/ethanent/centra/security/advisories/GHSA-v6cj-r88p-92rm
- https://github.com/advisories/GHSA-v6cj-r88p-92rm
- https://github.com/ethanent/centra
- https://snyk.io/vuln/SNYK-JS-CENTRA-536073
