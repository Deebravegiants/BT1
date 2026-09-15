# [H] @fastify/session reuses destroyed session cookie

## Summary
Severity: High
Advisory: GHSA-pj27-2xvp-4qxg
CVE: CVE-2024-35220
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-pj27-2xvp-4qxg
Type: github-advisory

## Affected
- npm: `@fastify/session` — affected >=0 <10.9.0

## Details
### Impact

When restoring the cookie from the session store, the `expires` field is overriden if the `maxAge` field was set.
This means a cookie is never correctly detected as expired and thus expired sessions are not destroyed.

### Patches

Updating to v10.9.0 will solve this.

### Workarounds

None

### References

Publicly reported at: https://github.com/fastify/session/issues/251

## References
- https://github.com/fastify/session/security/advisories/GHSA-pj27-2xvp-4qxg
- https://nvd.nist.gov/vuln/detail/CVE-2024-35220
- https://github.com/fastify/session/issues/251
- https://github.com/fastify/session/commit/0495ce5b534c4550f25228821db8098293439f2f
- https://github.com/fastify/session
