# [H] Missing Origin Validation in browserify-hmr

## Summary
Severity: High
Advisory: GHSA-77q4-m83q-w76v
CVE: CVE-2018-14730
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-77q4-m83q-w76v
Type: github-advisory

## Affected
- npm: `browserify-hmr` — affected >=0 <0.4.0

## Details
Versions of `browserify-hmr` prior to 0.4.0 are missing origin validation on the websocket server. 

This vulnerability allows a remote attacker to steal a developer's source code because the origin of requests to the websocket server that is used for Hot Module Replacement (HMR) are not validated.


## Recommendation

Upgrade to version 0.4.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14730
- https://github.com/AgentME/browserify-hmr/issues/41
- https://blog.cal1.cn/post/Sniffing%20Codes%20in%20Hot%20Module%20Reloading%20Messages
- https://blog.cal1.cn/post/Sniffing%20Codes%20in%20Hot%20Module%20Reloading%20Messages)
- https://github.com/AgentME/browserify-hmr
- https://www.npmjs.com/advisories/726
