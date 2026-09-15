# [H] aiohttp-session creates non-expiring sessions

## Summary
Severity: High
Advisory: GHSA-mr4x-c4v9-x729
CVE: CVE-2018-1000814
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-mr4x-c4v9-x729
Type: github-advisory

## Affected
- PyPI: `aiohttp-session` — affected >=0 <2.7.0

## Details
aio-libs aiohttp-session version 2.6.0 and earlier contains a Other/Unknown vulnerability in EncryptedCookieStorage and NaClCookieStorage that can result in Non-expiring sessions / Infinite lifespan. This attack appear to be exploitable via Recreation of a cookie post-expiry with the same value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000814
- https://github.com/aio-libs/aiohttp-session/issues/325
- https://github.com/aio-libs/aiohttp-session/pull/331
- https://github.com/aio-libs/aiohttp-session/commit/1b356f01bbab57d041c9a75bacd72fbbf8524728
- https://github.com/advisories/GHSA-mr4x-c4v9-x729
- https://github.com/aio-libs/aiohttp-session
- https://github.com/pypa/advisory-database/tree/main/vulns/aiohttp-session/PYSEC-2018-35.yaml
