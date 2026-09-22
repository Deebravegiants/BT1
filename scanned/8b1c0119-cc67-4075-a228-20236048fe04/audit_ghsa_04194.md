# [C] deepstream is vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-9v98-6g37-x9g6
CVE: CVE-2026-49252
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-9v98-6g37-x9g6
Type: github-advisory

## Affected
- npm: `@deepstream/server` — affected >=0 <10.0.5

## Details
### Impact
Prototype pollution in deepstream server v <=10.0.4. Potential privilege escalation from any authenticated user with write permission to any record.

### Patches
Yes, upgrade to v10.0.5

### Workarounds
Filter out all messages containing the path `__proto__`, `constructor`, `prototype`, **before they reach the server's message pipeline**

## References
- https://github.com/deepstreamIO/deepstream.io/security/advisories/GHSA-9v98-6g37-x9g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-49252
- https://github.com/deepstreamIO/deepstream.io/commit/54b8e2958a98df444b5b5d9a66e22872afd84e44
- https://github.com/deepstreamIO/deepstream.io
