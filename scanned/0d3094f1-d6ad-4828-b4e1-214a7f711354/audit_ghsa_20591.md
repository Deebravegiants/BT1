# [H] node-fetch forwards secure headers to untrusted sites

## Summary
Severity: High
Advisory: GHSA-r683-j2x4-v87g
CVE: CVE-2022-0235
CWE: CWE-173, CWE-200, CWE-601
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-r683-j2x4-v87g
Type: github-advisory

## Affected
- npm: `node-fetch` — affected >=3.0.0 <3.1.1
- npm: `node-fetch` — affected >=0 <2.6.7

## Details
node-fetch forwards secure headers such as `authorization`, `www-authenticate`, `cookie`, & `cookie2` when redirecting to a untrusted site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0235
- https://github.com/node-fetch/node-fetch/pull/1449/commits/5c32f002fdd65b1c6a8f1e3620210813d45c7e60
- https://github.com/node-fetch/node-fetch/pull/1453
- https://github.com/node-fetch/node-fetch/commit/1ef4b560a17e644a02a3bfdea7631ffeee578b35
- https://github.com/node-fetch/node-fetch/commit/36e47e8a6406185921e4985dcbeff140d73eaa10
- https://github.com/node-fetch/node-fetch/commit/5c32f002fdd65b1c6a8f1e3620210813d45c7e60
- https://cert-portal.siemens.com/productcert/pdf/ssa-637483.pdf
- https://github.com/node-fetch/node-fetch
- https://huntr.dev/bounties/d26ab655-38d6-48b3-be15-f9ad6b6ae6f7
- https://lists.debian.org/debian-lts-announce/2022/12/msg00007.html
