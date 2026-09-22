# [C] mockery is vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-gmwp-3pwc-3j3g
CVE: CVE-2022-37614
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-12
Source: https://github.com/advisories/GHSA-gmwp-3pwc-3j3g
Type: github-advisory

## Affected
- npm: `mockery` — affected >=0

## Details
Prototype pollution vulnerability in function enable in mockery.js in mfncooper mockery commit 822f0566fd6d72af8c943ae5ca2aa92e516aa2cf via the key variable in mockery.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37614
- https://github.com/mfncooper/mockery/issues/77
- https://github.com/mfncooper/mockery
- https://github.com/mfncooper/mockery/blob/822f0566fd6d72af8c943ae5ca2aa92e516aa2cf/mockery.js#L119
- https://github.com/mfncooper/mockery/blob/822f0566fd6d72af8c943ae5ca2aa92e516aa2cf/mockery.js#L62
