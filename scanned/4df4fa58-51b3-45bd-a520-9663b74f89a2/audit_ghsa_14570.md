# [M] keycloak-connect contains Open redirect vulnerability in the Node.js adapter

## Summary
Severity: Medium
Advisory: GHSA-59fq-727j-hm3f
CVE: CVE-2022-2237
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-02
Source: https://github.com/advisories/GHSA-59fq-727j-hm3f
Type: github-advisory

## Affected
- npm: `keycloak-connect` — affected >=0 <21.0.1

## Details
There is an Open Redirect vulnerability in the Node.js adapter when forwarding requests to Keycloak using `checkSSO` with query param `prompt=none`.

## References
- https://github.com/keycloak/keycloak-nodejs-connect/security/advisories/GHSA-59fq-727j-hm3f
- https://nvd.nist.gov/vuln/detail/CVE-2022-2237
- https://github.com/keycloak/keycloak-nodejs-connect/commit/190a9470e234bbd9ac5d5de43f5a19aead9a2c21
- https://bugzilla.redhat.com/show_bug.cgi?id=2097007
- https://github.com/keycloak/keycloak-nodejs-connect
