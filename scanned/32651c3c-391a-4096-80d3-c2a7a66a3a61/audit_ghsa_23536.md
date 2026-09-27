# [C] mxGraph vulnerable to XXE attacks

## Summary
Severity: Critical
Advisory: GHSA-wvpv-8524-wg6x
CVE: CVE-2017-18197
CWE: CWE-611
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wvpv-8524-wg6x
Type: github-advisory

## Affected
- npm: `mxgraph` — affected >=0 <3.7.6

## Details
In `mxGraphViewImageReader.java` in mxGraph before 3.7.6, the `SAXParserFactory` instance in `convert()` is missing flags to prevent XML External Entity (XXE) attacks, as demonstrated by `/ServerView`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18197
- https://github.com/jgraph/mxgraph/issues/124
- https://github.com/jgraph/mxgraph/commit/97b3718db64a6ca9afb3382de2926eb8da660052
- https://github.com/jgraph/mxgraph
- https://lists.debian.org/debian-lts-announce/2018/03/msg00002.html
