# [M] Unauthenticated Account Registration via /user/invited Bypasses All Signup Restrictions in Chartbrew

## Summary
Severity: Medium
Advisory: CVE-2026-35514
Aliases: GHSA-g47g-v5cp-j8hp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-35514
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. In version 4.9.0, the endpoint POST /user/invited does not validate any invite token, authentication header, or session. Any unauthenticated attacker can call this endpoint directly to create a fully active account and receive a valid JWT — even when the instance has existing users and signupRestricted is enabled. This bypass is distinct from the normal registration endpoint (POST /user) which enforces signupRestricted and sets active: false pending verification. This issue has been patched in version 5.0.0.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35514.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-g47g-v5cp-j8hp
- https://nvd.nist.gov/vuln/detail/CVE-2026-35514
