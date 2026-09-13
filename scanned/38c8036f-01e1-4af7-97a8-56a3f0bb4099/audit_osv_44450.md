# [H] Omnivore before android-0.227.0 Authentication Bypass via Apple Sign-in

## Summary
Severity: High
Advisory: CVE-2026-82454
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82454
Type: osv

## Details
The Omnivore API (packages/api) before the fix in commit abf53d6 contains an authentication bypass in Apple sign-in token verification. The decodeAppleToken function extracted the 'alg' field from the attacker-supplied JWT header and passed it as the sole allowed algorithm to jwt.verify(). Using jsonwebtoken v8 (which does not validate key/algorithm compatibility), an attacker can set alg=HS256 and sign a forged token using Apple's publicly available RSA public key as the HMAC secret, bypassing signature verification and impersonating any Apple-linked account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82454.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82454
- https://www.vulncheck.com/advisories/omnivore-before-android-0.227.0-authentication-bypass-via-apple-sign-in
- https://github.com/omnivore-app/omnivore/commit/abf53d6508755d3d22a994e28e370a9193ea977a
- https://github.com/omnivore-app/omnivore/pull/4652
- https://github.com/omnivore-app/omnivore
