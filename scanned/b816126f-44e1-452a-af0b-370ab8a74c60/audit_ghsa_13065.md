# [C] GitPython vulnerable to remote code execution due to insufficient sanitization of input arguments

## Summary
Severity: Critical
Advisory: GHSA-pr76-5cm5-w9cj
CVE: CVE-2023-40267
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-pr76-5cm5-w9cj
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.32

## Details
GitPython before 3.1.32 does not block insecure non-multi options in `clone` and `clone_from`, making it vulnerable to Remote Code Execution (RCE) due to improper user input validation, which makes it possible to inject a maliciously crafted remote URL into the clone command. Exploiting this vulnerability is possible because the library makes external calls to git without sufficient sanitization of input arguments. NOTE: this issue exists because of an incomplete fix for CVE-2022-24439.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40267
- https://github.com/gitpython-developers/GitPython/pull/1609
- https://github.com/gitpython-developers/GitPython/commit/ca965ecc81853bca7675261729143f54e5bf4cdd
- https://github.com/gitpython-developers/GitPython
- https://github.com/pypa/advisory-database/tree/main/vulns/gitpython/PYSEC-2023-137.yaml
- https://lists.debian.org/debian-lts-announce/2024/10/msg00030.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AV5DV7GBLMOZT7U3Q4TDOJO5R6G3V6GH
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF6AXUTC5BO7L2SBJMCVKJSPKWY52I5R
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AV5DV7GBLMOZT7U3Q4TDOJO5R6G3V6GH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PF6AXUTC5BO7L2SBJMCVKJSPKWY52I5R
