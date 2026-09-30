# [M] Several quadratic complexity bugs may lead to denial of service in Commonmarker

## Summary
Severity: Medium
Advisory: GHSA-636f-xm5j-pj9m
CWE: CWE-400
Ecosystem: RubyGems
Published: 2023-01-24
Source: https://github.com/advisories/GHSA-636f-xm5j-pj9m
Type: github-advisory

## Affected
- RubyGems: `commonmarker` — affected >=0 <0.23.7

## Details
## Impact

Several quadratic complexity bugs in commonmarker's underlying [`cmark-gfm`](https://github.com/github/cmark-gfm) library may lead to unbounded resource exhaustion and subsequent denial of service.

The following vulnerabilities were addressed:

* [CVE-2023-22483](https://github.com/github/cmark-gfm/security/advisories/GHSA-29g3-96g3-jg6c)
* [CVE-2023-22484](https://github.com/github/cmark-gfm/security/advisories/GHSA-24f7-9frr-5h2r)
* [CVE-2023-22485](https://github.com/github/cmark-gfm/security/advisories/GHSA-c944-cv5f-hpvr)
* [CVE-2023-22486](https://github.com/github/cmark-gfm/security/advisories/GHSA-r572-jvj2-3m8p)

For more information, consult the release notes for version [`0.23.0.gfm.7`](https://github.com/github/cmark-gfm/releases/tag/0.29.0.gfm.7).

## Mitigation

Users are advised to upgrade to commonmarker version [`0.23.7`](https://rubygems.org/gems/commonmarker/versions/0.23.7).

## References
- https://github.com/gjtorikian/commonmarker/security/advisories/GHSA-636f-xm5j-pj9m
- https://github.com/gjtorikian/commonmarker
