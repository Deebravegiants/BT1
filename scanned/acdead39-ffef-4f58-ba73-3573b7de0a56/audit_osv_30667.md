# [M] Algorithm Confusion Vulnerability in cjwt

## Summary
Severity: Medium
Advisory: CVE-2024-54150
Aliases: GHSA-9h24-7qp5-gp82
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-12-19
Source: https://osv.dev/vulnerability/CVE-2024-54150
Type: osv

## Details
cjwt is a C JSON Web Token (JWT) Implementation. Algorithm confusion occurs when a system improperly verifies the type of signature used, allowing attackers to exploit the lack of distinction between signing methods.  If the system doesn't differentiate between an HMAC signed token and an RS/EC/PS signed token during verification, it becomes vulnerable to this kind of attack. For instance, an attacker could craft a token with the alg field set to "HS256" while the server expects an asymmetric algorithm like "RS256". The server might mistakenly use the wrong verification method, such as using a public key as the HMAC secret, leading to unauthorised access. For RSA, the key can be computed from a few signatures. For Elliptic Curve (EC), two potential keys can be recovered from one signature. This can be used to bypass the signature mechanism if an application relies on asymmetrically signed tokens. This issue has been addressed in version 2.3.0 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54150.json
- https://github.com/xmidt-org/cjwt/security/advisories/GHSA-9h24-7qp5-gp82
- https://nvd.nist.gov/vuln/detail/CVE-2024-54150
- https://github.com/xmidt-org/cjwt/commit/096ab3e37f73c914b716e7259589179f363265fd
