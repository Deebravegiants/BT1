# [H] Webargs mishandles concurrent JSON parsing

## Summary
Severity: High
Advisory: GHSA-8554-jxcw-454q
CVE: CVE-2019-9710
CWE: CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-03-12
Source: https://github.com/advisories/GHSA-8554-jxcw-454q
Type: github-advisory

## Affected
- PyPI: `webargs` — affected >=0 <5.1.3

## Details
An issue was discovered in webargs before 5.1.3, as used with marshmallow and other products. JSON parsing uses a short-lived cache to store the parsed JSON body. This cache is not thread-safe, meaning that incorrect JSON payloads could have been parsed for concurrent requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9710
- https://github.com/marshmallow-code/webargs/issues/371
- https://github.com/marshmallow-code/webargs/pull/373
- https://github.com/marshmallow-code/webargs/commit/716bd8d1f24c84aaf99170efaa17d1d34206f6c0
- https://github.com/marshmallow-code/webargs
- https://github.com/pypa/advisory-database/tree/main/vulns/webargs/PYSEC-2019-139.yaml
- https://webargs.readthedocs.io/en/latest/changelog.html
- https://webargs.readthedocs.io/en/latest/changelog.html#id24
