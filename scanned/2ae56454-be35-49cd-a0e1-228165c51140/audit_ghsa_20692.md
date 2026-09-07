# [M] node-fetch Inefficient Regular Expression Complexity 

## Summary
Severity: Medium
Advisory: GHSA-vp56-6g26-6827
CVE: CVE-2022-2596
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-02
Source: https://github.com/advisories/GHSA-vp56-6g26-6827
Type: github-advisory

## Affected
- npm: `node-fetch` — affected >=3.0.0 <3.2.10

## Details
[node-fetch](https://www.npmjs.com/package/node-fetch) is a light-weight module that brings window.fetch to node.js.

Affected versions of this package are vulnerable to Regular Expression Denial of Service (ReDoS) in the `isOriginPotentiallyTrustworthy()` function in `referrer.js`, when processing a URL string with alternating letters and periods, such as `'http://' + 'a.a.'.repeat(i) + 'a'`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2596
- https://github.com/node-fetch/node-fetch/pull/1611
- https://github.com/node-fetch/node-fetch/commit/28802387292baee467e042e168d92597b5bbbe3d
- https://github.com/node-fetch/node-fetch
- https://github.com/node-fetch/node-fetch/releases/tag/v3.2.10
- https://huntr.dev/bounties/a7e6a136-0a4b-46c4-ad20-802f1dd60bf7
