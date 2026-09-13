# [H] LibJWT: Algorithm confusion allows JWT forgery with RSA JWK as empty-key HMAC

## Summary
Severity: High
Advisory: CVE-2026-44699
Aliases: GHSA-q843-6q5f-w55g
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-44699
Type: osv

## Details
LibJWT is a C JSON Web Token Library. From 3.0.0 to 3.3.2, libjwt accepts an RSA JWK that does not contain an alg parameter as the verification key for an HS256/HS384/HS512 token. In the OpenSSL backend, this causes HMAC verification to run with a zero-length key, so an attacker can forge a valid JWT without knowing any secret or RSA private key. This is an algorithm-confusion authentication bypass. It affects applications that load RSA keys from JWKS where alg is omitted, which is valid JWK syntax and common in real deployments, and then choose the verification algorithm from the JWT header, for example in a kid lookup callback. This vulnerability is fixed in 3.3.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44699.json
- https://github.com/benmcollins/libjwt/security/advisories/GHSA-q843-6q5f-w55g
- https://nvd.nist.gov/vuln/detail/CVE-2026-44699
