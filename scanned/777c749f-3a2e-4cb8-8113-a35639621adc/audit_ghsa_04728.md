# [M] AIOHTTP is Vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Medium
Advisory: GHSA-jg22-mg44-37j8
CVE: CVE-2026-34993
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-jg22-mg44-37j8
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.14.0

## Details
### Summary

Using ``CookieJar.load()`` with untrusted input may allow arbitrary code execution.

### Impact

Most applications using this function will be doing so with the user's own data, so this is unlikely to affect many applications.

### Workaround

If an application does allow attacker controlled files to be loaded, a workaround on older releases would be to sanitise the files before loading.

-----

Patch: https://github.com/aio-libs/aiohttp/commit/dcf40f30637e8752c76781cf6703b5a236749a00

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-jg22-mg44-37j8
- https://nvd.nist.gov/vuln/detail/CVE-2026-34993
- https://github.com/aio-libs/aiohttp/commit/dcf40f30637e8752c76781cf6703b5a236749a00
- https://github.com/aio-libs/aiohttp
