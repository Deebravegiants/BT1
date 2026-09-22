# [H] minimatch ReDoS vulnerability

## Summary
Severity: High
Advisory: GHSA-f8q6-p94x-37v3
CVE: CVE-2022-3517
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-18
Source: https://github.com/advisories/GHSA-f8q6-p94x-37v3
Type: github-advisory

## Affected
- npm: `minimatch` — affected >=0 <3.0.5

## Details
A vulnerability was found in the minimatch package. This flaw allows a Regular Expression Denial of Service (ReDoS) when calling the braceExpand function with specific arguments, resulting in a Denial of Service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3517
- https://github.com/grafana/grafana-image-renderer/issues/329
- https://github.com/nodejs/node/issues/42510
- https://github.com/isaacs/minimatch/commit/a8763f4388e51956be62dc6025cec1126beeb5e6
- https://github.com/isaacs/minimatch
- https://lists.debian.org/debian-lts-announce/2023/01/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MTEUUTNIEBHGKUKKLNUZSV7IEP6IP3Q3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UM6XJ73Q3NAM5KSGCOKJ2ZIA6GUWUJLK
