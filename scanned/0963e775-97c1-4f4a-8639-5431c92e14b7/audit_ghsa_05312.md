# [M] aiohttp: DigestAuthMiddleware Applies Credentials to Cross-Origin Redirect Challenges

## Summary
Severity: Medium
Advisory: GHSA-hpj7-wq8m-9hgp
CVE: CVE-2026-54276
CWE: CWE-200, CWE-522
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-hpj7-wq8m-9hgp
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.1

## Details
### Summary

``DigestAuthMiddleware`` can send an authentication response after following a cross-origin redirect.

### Impact

If the client follows a redirect (the default option) to an attacker controlled domain, the attacker may be able to extract the auth digest.

This likely requires an open redirect vulnerability or similar on the target domain for an attacker to be able to execute. Further, the attacker is only receiving the digest, so should only be able to extract the user's credentials if the cryptography is weak or there is some kind of password reuse.

### Workaround

Disable ``follow_redirects`` if this is a concern.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/38d16060037e1bfcd6d677abababa3c2a4bb58fa

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-hpj7-wq8m-9hgp
- https://github.com/aio-libs/aiohttp/commit/38d16060037e1bfcd6d677abababa3c2a4bb58fa
- https://github.com/aio-libs/aiohttp
