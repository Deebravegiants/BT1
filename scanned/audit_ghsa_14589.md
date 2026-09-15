# [M] redis-py Race Condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-24wv-mv5m-xv4h
CVE: CVE-2023-28858
CWE: CWE-193
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-03-26
Source: https://github.com/advisories/GHSA-24wv-mv5m-xv4h
Type: github-advisory

## Affected
- PyPI: `redis` — affected >=4.4.0 <4.4.3
- PyPI: `redis` — affected >=4.5.0 <4.5.3
- PyPI: `redis` — affected >=4.2.0 <4.3.6

## Details
redis-py before 4.5.3, as used in ChatGPT and other products, leaves a connection open after canceling an async Redis command at an inopportune time (in the case of a pipeline operation), and can send response data to the client of an unrelated request in an off-by-one manner. The fixed versions for this CVE Record are 4.3.6, 4.4.3, and 4.5.3, but [are believed to be incomplete](https://github.com/redis/redis-py/issues/2665). CVE-2023-28859 has been assigned the issues caused by the incomplete fixes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28858
- https://github.com/redis/redis-py/issues/2624
- https://github.com/redis/redis-py/pull/2641
- https://github.com/redis/redis-py/commit/d56baeb683fc1935cfa343fa2eeb0fa9bd955283
- https://github.com/pypa/advisory-database/tree/main/vulns/redis/PYSEC-2023-45.yaml
- https://github.com/redis/redis-py
- https://github.com/redis/redis-py/compare/v4.3.5...v4.3.6
- https://github.com/redis/redis-py/compare/v4.4.2...v4.4.3
- https://github.com/redis/redis-py/compare/v4.5.2...v4.5.3
- https://github.com/redis/redis-py/releases/tag/v4.4.4
- https://github.com/redis/redis-py/releases/tag/v4.5.4
- https://openai.com/blog/march-20-chatgpt-outage
