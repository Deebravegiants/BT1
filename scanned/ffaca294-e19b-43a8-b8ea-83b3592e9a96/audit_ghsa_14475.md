# [H] redis-py Race Condition due to incomplete fix

## Summary
Severity: High
Advisory: GHSA-8fww-64cx-x8p5
CVE: CVE-2023-28859
CWE: CWE-459
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-26
Source: https://github.com/advisories/GHSA-8fww-64cx-x8p5
Type: github-advisory

## Affected
- PyPI: `redis` — affected >=4.5.0 <4.5.4
- PyPI: `redis` — affected >=4.2.0 <4.4.4

## Details
redis-py through 4.5.3 and 4.4.3 leaves a connection open after canceling an async Redis command at an inopportune time (in the case of a non-pipeline operation), and can send response data to the client of an unrelated request. NOTE: this issue exists because of an incomplete fix for CVE-2023-28858.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28859
- https://github.com/redis/redis-py/issues/2665
- https://github.com/redis/redis-py/pull/1899
- https://github.com/redis/redis-py/pull/2641
- https://github.com/redis/redis-py/pull/2666
- https://github.com/redis/redis-py/pull/2671
- https://github.com/redis/redis-py/commit/66a4d6b2a493dd3a20cc299ab5fef3c14baad965
- https://github.com/redis/redis-py/commit/b3c89acd0ffe8303649ad8207bc911b1d6a033eb
- https://github.com/pypa/advisory-database/tree/main/vulns/redis/PYSEC-2023-46.yaml
- https://github.com/redis/redis-py
- https://github.com/redis/redis-py/releases/tag/v4.4.4
- https://github.com/redis/redis-py/releases/tag/v4.5.4
