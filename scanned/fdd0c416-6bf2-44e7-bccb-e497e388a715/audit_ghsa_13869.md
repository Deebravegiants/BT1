# [H] Regular Expression Denial of Service in simple-markdown

## Summary
Severity: High
Advisory: GHSA-gpvj-gp8c-c7p2
CVE: CVE-2019-25103
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-12
Source: https://github.com/advisories/GHSA-gpvj-gp8c-c7p2
Type: github-advisory

## Affected
- npm: `simple-markdown` — affected >=0 <0.5.2

## Details
A vulnerability has been found in simple-markdown 0.5.1 and classified as problematic. Affected by this vulnerability is an unknown functionality of the file simple-markdown.js. The manipulation leads to inefficient regular expression complexity. The attack can be launched remotely. Upgrading to version 0.5.2 is able to address this issue. The name of the patch is 89797fef9abb4cab2fb76a335968266a92588816. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-220639.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25103
- https://github.com/Khan/simple-markdown/issues/71
- https://github.com/ariabuckles/simple-markdown/commit/89797fef9abb4cab2fb76a335968266a92588816
- https://github.com/ariabuckles/simple-markdown
- https://github.com/ariabuckles/simple-markdown/releases/tag/0.5.2
- https://snyk.io/vuln/SNYK-JS-SIMPLEMARKDOWN-460540
- https://vuldb.com/?ctiid.220639
- https://vuldb.com/?id.220639
