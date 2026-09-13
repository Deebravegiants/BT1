# [M] CVE-2021-32631

## Summary
Severity: Medium
Advisory: CVE-2021-32631
Aliases: GHSA-fjq8-896w-pv28
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-07-26
Source: https://osv.dev/vulnerability/CVE-2021-32631
Type: osv

## Details
Common is a package of common modules that can be accessed by NIMBLE services. Common before commit number 3b96cb0293d3443b870351945f41d7d55cb34b53 did not properly verify the signature of JSON Web Tokens. This allows someone to forge a valid JWT. Being able to forge JWTs may lead to authentication bypasses. Commit number 3b96cb0293d3443b870351945f41d7d55cb34b53 contains a patch for the issue. As a workaround, one may use the parseClaimsJws method to correctly verify the signature of a JWT.

## References
- https://github.com/nimble-platform/common/security/advisories/GHSA-fjq8-896w-pv28
- https://github.com/nimble-platform/common/commit/12197a755bd524559bf4e16475595a2c6fcd34db
- https://github.com/nimble-platform/common/commit/3b96cb0293d3443b870351945f41d7d55cb34b53
- https://github.com/nimble-platform/common/commit/a59ad46733912a5580530e39cac0e6ebc83cc563
