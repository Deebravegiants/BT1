# [H] Unlimited consumption of resources in @fastify/multipart

## Summary
Severity: High
Advisory: GHSA-27c6-mcxv-x3fh
CVE: CVE-2025-24033
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-23
Source: https://github.com/advisories/GHSA-27c6-mcxv-x3fh
Type: github-advisory

## Affected
- npm: `@fastify/multipart` — affected >=0 <8.3.1
- npm: `@fastify/multipart` — affected >=9.0.0 <9.0.3

## Details
### Impact

The `saveRequestFiles` function does not delete the uploaded temporary files when user cancels the request.

### Patches

Fixed in version 8.3.1 and 9.0.3

### Workarounds

Do not use `saveRequestFiles`.

### References

This was identified in https://github.com/fastify/fastify-multipart/issues/546 and fixed in https://github.com/fastify/fastify-multipart/pull/567.

## References
- https://github.com/fastify/fastify-multipart/security/advisories/GHSA-27c6-mcxv-x3fh
- https://nvd.nist.gov/vuln/detail/CVE-2025-24033
- https://github.com/fastify/fastify-multipart/issues/546
- https://github.com/fastify/fastify-multipart/pull/567
- https://github.com/fastify/fastify-multipart
