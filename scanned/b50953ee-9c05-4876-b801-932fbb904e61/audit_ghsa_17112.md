# [M] @workos-inc/authkit-nextjs session replay vulnerability

## Summary
Severity: Medium
Advisory: GHSA-35w3-6qhc-474v
CVE: CVE-2024-29901
CWE: CWE-294
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-35w3-6qhc-474v
Type: github-advisory

## Affected
- npm: `@workos-inc/authkit-nextjs` — affected >=0 <0.4.2

## Details
### Impact

A user can reuse an expired session by controlling the `x-workos-session` header.

### Patches

Patched in https://github.com/workos/authkit-nextjs/releases/tag/v0.4.2

## References
- https://github.com/workos/authkit-nextjs/security/advisories/GHSA-35w3-6qhc-474v
- https://nvd.nist.gov/vuln/detail/CVE-2024-29901
- https://github.com/workos/authkit-nextjs/commit/6c3f4f3179d66cbb15de3962792083ff3b244a01
- https://github.com/workos/authkit-nextjs
- https://github.com/workos/authkit-nextjs/releases/tag/v0.4.2
