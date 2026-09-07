# [C] Blogifier does not properly restrict APIs

## Summary
Severity: Critical
Advisory: GHSA-qcx4-gfh8-w5p5
CVE: CVE-2019-12277
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qcx4-gfh8-w5p5
Type: github-advisory

## Affected
- NuGet: `Blogifier.Core` — affected >=0 <2.5.5

## Details
Blogifier 2.3 before 2019-05-11 does not properly restrict APIs, as demonstrated by missing checks for `..` in a pathname.

The issue is patched in the `2.4` branch, but `2.5.5` is the lowest available patched version on https://www.nuget.org/packages/Blogifier.Core.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12277
- https://github.com/blogifierdotnet/Blogifier/commit/3e2ae11f6be8aab82128f223c2916fab5a408be5
- https://github.com/blogifierdotnet/Blogifier
