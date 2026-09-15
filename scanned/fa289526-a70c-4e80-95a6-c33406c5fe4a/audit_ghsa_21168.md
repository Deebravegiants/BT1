# [C] thenify before 3.3.1 made use of unsafe calls to `eval`.

## Summary
Severity: Critical
Advisory: GHSA-29xr-v42j-r956
CVE: CVE-2020-7677
CWE: CWE-78
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-18
Source: https://github.com/advisories/GHSA-29xr-v42j-r956
Type: github-advisory

## Affected
- npm: `thenify` — affected >=0 <3.3.1
- Maven: `org.webjars.npm:thenify` — affected >=0 <3.3.1

## Details
Versions of thenify prior to 3.3.1 made use of unsafe calls to `eval`. Untrusted user input could thus lead to arbitrary code execution on the host. The patch in version 3.3.1 removes calls to `eval`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7677
- https://github.com/thenables/thenify/issues/29
- https://github.com/thenables/thenify/commit/0d94a24eb933bc835d568f3009f4d269c4c4c17a
- https://github.com/thenables/thenify
- https://github.com/thenables/thenify/blob/master/index.js%23L17
- https://lists.debian.org/debian-lts-announce/2022/09/msg00039.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MTEUUTNIEBHGKUKKLNUZSV7IEP6IP3Q3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UM6XJ73Q3NAM5KSGCOKJ2ZIA6GUWUJLK
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-572317
- https://security.snyk.io/vuln/SNYK-JS-THENIFY-571690
