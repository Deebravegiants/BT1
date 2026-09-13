# [H] Missing Origin Validation in parcel-bundler

## Summary
Severity: High
Advisory: GHSA-37q6-576q-vgr7
CVE: CVE-2018-14731
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-30
Source: https://github.com/advisories/GHSA-37q6-576q-vgr7
Type: github-advisory

## Affected
- npm: `parcel-bundler` — affected >=0 <1.10.0

## Details
Versions of `parcel-bundler` before 1.10.0 are missing origin validation on the websocket server. This vulnerability allows a remote attacker to steal a developer's source code because the origin of requests to the websocket server that is used for Hot Module Replacement (HMR) are not validated.


## Recommendation

Update to version 1.10.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14731
- https://github.com/parcel-bundler/parcel/issues/1783
- https://github.com/parcel-bundler/parcel/pull/1794
- https://github.com/parcel-bundler/parcel/commit/066e0bf6bd26b15c78bd47df023452e4b20073e4
- https://blog.cal1.cn/post/Sniffing%20Codes%20in%20Hot%20Module%20Reloading%20Messages
- https://blog.cal1.cn/post/Sniffing%20Codes%20in%20Hot%20Module%20Reloading%20Messages)
- https://github.com/advisories/GHSA-37q6-576q-vgr7
- https://github.com/parcel-bundler/parcel
- https://www.npmjs.com/advisories/721
