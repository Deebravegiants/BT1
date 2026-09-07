# [M] Invalid Curve Attack in node-jose

## Summary
Severity: Medium
Advisory: GHSA-rvj9-8cvx-3vq9
CVE: CVE-2017-16007
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-20
Source: https://github.com/advisories/GHSA-rvj9-8cvx-3vq9
Type: github-advisory

## Affected
- npm: `node-jose` — affected >=0 <0.9.3

## Details
Affected versions of `node-jose` are vulnerable to an invalid curve attack. This allows an attacker to recover the private secret key when JWE with Key Agreement with Elliptic Curve Diffie-Hellman Ephemeral Static (ECDH-ES) is used.

[Proof of Concept](https://gist.github.com/asanso/fa25685348051ef6a28d49aa0f27a4ae)


## Recommendation

Update to version 0.9.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16007
- https://github.com/cisco/node-jose/pull/88
- https://github.com/cisco/node-jose/commit/f92cffb4a0398b4b1158be98423369233282e0af
- https://gist.github.com/asanso/fa25685348051ef6a28d49aa0f27a4ae
- https://github.com/cisco/node-jose
- https://github.com/cisco/node-jose/compare/0.9.2...0.9.3
- http://blog.intothesymmetry.com/2017/03/critical-vulnerability-in-json-web.html
