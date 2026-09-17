# [C] Dulwich RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-cwwh-4382-6fwr
CVE: CVE-2017-16228
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cwwh-4382-6fwr
Type: github-advisory

## Affected
- PyPI: `dulwich` — affected >=0 <0.18.5

## Details
Dulwich before 0.18.5, when an SSH subprocess is used, allows remote attackers to execute arbitrary commands via an ssh URL with an initial dash character in the hostname, a related issue to CVE-2017-9800, CVE-2017-12836, CVE-2017-12976, CVE-2017-1000116, and CVE-2017-1000117.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16228
- https://github.com/jelmer/dulwich/commit/7116a0cbbda571f7dac863f4b1c00b6e16d6d8d6
- https://github.com/jelmer/dulwich
- https://github.com/pypa/advisory-database/tree/main/vulns/dulwich/PYSEC-2017-12.yaml
- https://tracker.debian.org/news/882440
- https://web.archive.org/web/20201220231743/https://www.dulwich.io/code/dulwich/commit/7116a0cbbda571f7dac863f4b1c00b6e16d6d8d6
- https://web.archive.org/web/20210128154006/https://www.dulwich.io/code/dulwich
- https://www.dulwich.io/code/dulwich
- https://www.dulwich.io/code/dulwich/commit/7116a0cbbda571f7dac863f4b1c00b6e16d6d8d6
