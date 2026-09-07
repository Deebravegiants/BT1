# [M] matrix-js-sdk has insufficient MXC URI validation which allows client-side path traversal

## Summary
Severity: Medium
Advisory: GHSA-xvg8-m4x3-w6xr
CVE: CVE-2024-50336
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2024-11-12
Source: https://github.com/advisories/GHSA-xvg8-m4x3-w6xr
Type: github-advisory

## Affected
- npm: `matrix-js-sdk` — affected >=0 <34.11.1

## Details
### Summary

matrix-js-sdk before 34.11.0 is vulnerable to client-side path traversal via crafted MXC URIs. A malicious room member can trigger clients based on the matrix-js-sdk to issue arbitrary authenticated GET requests to the client's homeserver.

### Details

The Matrix specification demands homeservers to [perform validation](https://spec.matrix.org/v1.12/client-server-api/#security-considerations-5) of the `server-name` and `media-id` components of MXC URIs with the intent to prevent path traversal. However, it is not mentioned that a similar check must also be performed on the client to prevent *client-side* path traversal. matrix-js-sdk fails to perform this validation.

### Patches

Fixed in matrix-js-sdk 34.11.1.

### Workarounds

None.

### References

- https://spec.matrix.org/v1.12/client-server-api/#security-considerations-5
- https://blog.doyensec.com/2024/07/02/cspt2csrf.html

## References
- https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-xvg8-m4x3-w6xr
- https://nvd.nist.gov/vuln/detail/CVE-2024-50336
- https://github.com/matrix-org/matrix-js-sdk
- https://lists.debian.org/debian-lts-announce/2025/01/msg00004.html
- https://spec.matrix.org/v1.12/client-server-api/#security-considerations-5
