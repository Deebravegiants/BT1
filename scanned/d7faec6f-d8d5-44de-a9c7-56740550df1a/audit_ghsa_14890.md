# [M] gqlparser denial of service vulnerability via the parserDirectives function

## Summary
Severity: Medium
Advisory: GHSA-2hmf-46v7-v6fx
CVE: CVE-2023-49559
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-06-12
Source: https://github.com/advisories/GHSA-2hmf-46v7-v6fx
Type: github-advisory

## Affected
- Go: `github.com/vektah/gqlparser/v2` — affected >=0 <2.5.14
- Go: `github.com/vektah/gqlparser` — affected >=0 <2.5.14

## Details
An issue in vektah gqlparser open-source-library v.2.5.10 allows a remote attacker to cause a denial of service via a crafted script to the parserDirectives function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49559
- https://github.com/99designs/gqlgen/issues/3118
- https://github.com/vektah/gqlparser/commit/36a3658873bf5a107f42488dfc392949cdd02977
- https://gist.github.com/uvzz/d3ed9d4532be16ec1040a2cf3dfec8d1
- https://github.com/advisories/GHSA-2hmf-46v7-v6fx
- https://github.com/vektah/gqlparser
- https://github.com/vektah/gqlparser/blob/master/parser/query.go#L316
