# [H] Path Traversal in Caucho Resin

## Summary
Severity: High
Advisory: GHSA-4w2q-9hp2-vxj5
CVE: CVE-2021-44138
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-05
Source: https://github.com/advisories/GHSA-4w2q-9hp2-vxj5
Type: github-advisory

## Affected
- Maven: `com.caucho:resin` — affected >=4.0.52

## Details
There is a Directory traversal vulnerability in Caucho Resin, as distributed in Resin 4.0.52 - 4.0.56, which allows remote attackers to read files in arbitrary directories via a ; in a pathname within an HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44138
- https://github.com/maybe-why-not/reponame/issues/2
