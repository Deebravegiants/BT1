# [M] Arbitrary remote file read in Wrangler dev server

## Summary
Severity: Medium
Advisory: GHSA-cfph-4qqh-w828
CVE: CVE-2023-7079
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-cfph-4qqh-w828
Type: github-advisory

## Affected
- npm: `wrangler` — affected >=3.9.0 <3.19.0

## Details
### Impact
Sending specially crafted HTTP requests and inspector messages to Wrangler's dev server could result in any file on the user's computer being accessible over the local network. An attacker that could trick any user on the local network into opening a malicious website could also read any file.

### Patches
This issue was fixed in `wrangler@3.19.0`. Wrangler will now only serve files that are part of your bundle, or referenced by your bundle's source maps.

### Workarounds
Configure Wrangler to listen on local interfaces instead with `wrangler dev --ip 127.0.0.1`. This is the [default as of `wrangler@3.16.0`](https://github.com/cloudflare/workers-sdk/security/advisories/GHSA-f8mp-x433-5wpf), and removes the local network as an attack vector, but does not prevent an attack from visiting a malicious website.

### References
- https://github.com/cloudflare/workers-sdk/pull/4532
- https://github.com/cloudflare/workers-sdk/pull/4535

## References
- https://github.com/cloudflare/workers-sdk/security/advisories/GHSA-cfph-4qqh-w828
- https://nvd.nist.gov/vuln/detail/CVE-2023-7079
- https://github.com/cloudflare/workers-sdk/pull/4532
- https://github.com/cloudflare/workers-sdk/pull/4535
- https://github.com/cloudflare/workers-sdk/commit/29df8e17545bf3926b6d61678b596be809d40c6d
- https://github.com/cloudflare/workers-sdk/commit/311ffbd5064f8301ac6f0311bbe5630897923b93
- https://github.com/cloudflare/workers-sdk
