# [M] Authlib: Cross-site request forging when using cache

## Summary
Severity: Medium
Advisory: GHSA-jj8c-mmj3-mmgv
CVE: CVE-2026-41425
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-jj8c-mmj3-mmgv
Type: github-advisory

## Affected
- PyPI: `authlib` — affected >=0 <1.6.11

## Details
### Summary

There is no CSRF protection on the cache feature on most integrations clients.

### Details
In `authlib.integrations.starlette_client.OAuth`, no CSRF protection is set up when using the cache parameter. When _not_ using the cache parameter, the use of SessionMiddleware ties the client to the auth state, preventing CSRF attacks. With the cache, there is no such mechanism. Other integratons have the same issue, it's not just starlette.

The state parameter is taken from the callback URL and the state is fetched from the cache without checking that it is the same client calling the redirect endpoint as was the one that initiated the auth flow.

This issue is documented in RFC 6749 section 10.12:
https://datatracker.ietf.org/doc/html/rfc6749#section-10.12

### PoC
- Set up a Starlette integration with a cache
- The attacker starts the auth flow up until before the callback URL is followed.
- The attacked sends the redirect URL to the victim
- The victim now completes the authorisation

### Impact
This impacts all users that use the cache to store auth state.

All users will be vulnerable to CSRF attacks and may have an attacker's account tied to their own.

## References
- https://github.com/authlib/authlib/security/advisories/GHSA-jj8c-mmj3-mmgv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41425
- https://github.com/authlib/authlib
- https://github.com/pypa/advisory-database/tree/main/vulns/authlib/PYSEC-2026-25.yaml
