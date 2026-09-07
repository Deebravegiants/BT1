# [H] aiohttp-session Session Fixation vulnerability

## Summary
Severity: High
Advisory: GHSA-fpwp-69xv-c67f
CVE: CVE-2018-1000519
CWE: CWE-384
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-09-13
Source: https://github.com/advisories/GHSA-fpwp-69xv-c67f
Type: github-advisory

## Affected
- PyPI: `aiohttp-session` — affected >=0 <2.4.0

## Details
The pypi package aiohttp-session before 2.4.0 contained a Session Fixation vulnerability in `load_session` function for RedisStorage that can result in Session Hijacking. This attack appear to be exploitable via Any method that allows setting session cookies (`?session=<>`, or meta tags or script tags with Set-Cookie).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000519
- https://github.com/aio-libs/aiohttp-session/issues/272
- https://github.com/aio-libs/aiohttp-session/commit/6b7864004d3442dbcfaf8687f63262c1c629f569
- https://github.com/advisories/GHSA-fpwp-69xv-c67f
- https://github.com/aio-libs/aiohttp-session
- https://github.com/aio-libs/aiohttp-session/blob/master/aiohttp_session/redis_storage.py#L60
- https://github.com/pypa/advisory-database/tree/main/vulns/aiohttp-session/PYSEC-2018-80.yaml
