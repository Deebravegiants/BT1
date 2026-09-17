# [M] Supabase Auth has insecure Apple and Azure authentication with ID tokens

## Summary
Severity: Medium
Advisory: CVE-2026-31813
Aliases: GHSA-v36f-qvww-8w8m
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31813
Type: osv

## Details
Supabase Auth is a JWT based API for managing users and issuing JWT tokens. Prior to 2.185.0, a vulnerability has been identified that allows an attacker to issue sessions for arbitrary users using specially crafted ID tokens when the Apple or Azure providers are enabled. The attacker issues a valid, asymmetrically signed ID token from their issuer for each victim email address, which then is sent to the Supabase Auth token endpoint using the ID token flow. If the ID token is OIDC compliant, the Auth server would validate it against the attacker-controlled issuer and link the existing OIDC identity (Apple or Azure) of the victim to an additional OIDC identity based on the ID token contents. The Auth server would then issue a valid user session (access and refresh tokens) at the AAL1 level to the attacker. This vulnerability is fixed in 2.185.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31813.json
- https://github.com/supabase/auth/security/advisories/GHSA-v36f-qvww-8w8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-31813
