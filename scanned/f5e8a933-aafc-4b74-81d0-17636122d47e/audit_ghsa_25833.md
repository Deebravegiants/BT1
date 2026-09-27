# [C] Arbitrary code execution in post-loader

## Summary
Severity: Critical
Advisory: GHSA-66ww-999q-mffq
CVE: CVE-2022-0748
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-66ww-999q-mffq
Type: github-advisory

## Affected
- npm: `post-loader` — affected >=0.0.0

## Details
post-loader is webpack loader for blog posts written in Markdown. The package post-loader from 0.0.0 is vulnerable to Arbitrary Code Execution which uses a markdown parser in an unsafe way so that any javascript code inside the markdown input files gets evaluated and executed. At this time, there is no known workaround or patch available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0748
- https://github.com/egoist/post-loader
- https://snyk.io/vuln/SNYK-JS-POSTLOADER-2403737
