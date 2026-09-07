# [M] OpenStack Keystone's federated token rescoping mechanism doesn't propagate the original token's expiry to the newly issued token

## Summary
Severity: Medium
Advisory: GHSA-whqr-fgm5-x77q
CVE: CVE-2026-44394
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-whqr-fgm5-x77q
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=14.0.0 <27.0.2
- PyPI: `keystone` — affected >=28.0.0 <28.0.2
- PyPI: `keystone` — affected >=29.0.0 <29.0.2

## Details
An issue was discovered in OpenStack Keystone before 29.0.2. The Keystone federated token rescoping mechanism does not propagate the original token's expiry to the newly issued token. When a federated user rescopes a token via POST /v3/auth/tokens, the handle_scoped_token() function in the mapped authentication plugin returns response data without an expires_at value. The token provider falls back to issuing a token with a fresh default TTL. By rescoping repeatedly before each token expires, a user can maintain access indefinitely, bypassing operator-configured token lifetime policies. This is a variant of CVE-2012-3426. Only deployments using federated identity (SAML2, OpenID Connect) are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44394
- https://bugs.launchpad.net/keystone/+bug/2150379
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2026-603.yaml
- https://security.openstack.org/ossa/OSSA-2026-015.html
