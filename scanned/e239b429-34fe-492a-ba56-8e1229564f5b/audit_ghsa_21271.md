# [C] Prototype pollution in webpack loader-utils

## Summary
Severity: Critical
Advisory: GHSA-76p3-8jx3-jpfq
CVE: CVE-2022-37601
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-13
Source: https://github.com/advisories/GHSA-76p3-8jx3-jpfq
Type: github-advisory

## Affected
- npm: `loader-utils` — affected >=2.0.0 <2.0.3
- npm: `loader-utils` — affected >=0 <1.4.1

## Details
Prototype pollution vulnerability in function parseQuery in parseQuery.js in webpack loader-utils prior to version 2.0.3 via the name variable in parseQuery.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37601
- https://github.com/webpack/loader-utils/issues/212
- https://github.com/webpack/loader-utils/issues/212#issuecomment-1319192884
- https://github.com/xmldom/xmldom/issues/436#issuecomment-1319412826
- https://github.com/webpack/loader-utils/pull/217
- https://github.com/webpack/loader-utils/pull/220
- https://github.com/webpack/loader-utils/commit/4504e34c4796a5836ef70458327351675aed48a5
- https://github.com/webpack/loader-utils/commit/a93cf6f4702012030f6b5ee8340d5c95ec1c7d4c
- https://github.com/webpack/loader-utils/commit/f4e48a232fae900237c3e5ff7b57ce9e1c734de1
- https://dl.acm.org/doi/abs/10.1145/3488932.3497769
- https://dl.acm.org/doi/pdf/10.1145/3488932.3497769
- https://github.com/webpack/loader-utils
- https://github.com/webpack/loader-utils/releases/tag/v1.4.1
- https://github.com/webpack/loader-utils/releases/tag/v2.0.3
- https://lists.debian.org/debian-lts-announce/2022/12/msg00044.html
- http://users.encs.concordia.ca/~mmannan/publications/JS-vulnerability-aisaccs2022.pdf
