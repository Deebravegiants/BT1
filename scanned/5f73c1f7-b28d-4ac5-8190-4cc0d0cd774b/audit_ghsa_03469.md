# [H] Node-Redis potential exponential regex in monitor mode

## Summary
Severity: High
Advisory: GHSA-35q2-47q7-3pc3
CVE: CVE-2021-29469
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-27
Source: https://github.com/advisories/GHSA-35q2-47q7-3pc3
Type: github-advisory

## Affected
- npm: `redis` — affected >=2.6.0 <3.1.1

## Details
### Impact
When a client is in monitoring mode, the regex begin used to detected monitor messages could cause exponential backtracking on some strings. This issue could lead to a denial of service.

### Patches
The problem was fixed in commit [`2d11b6d`](https://github.com/NodeRedis/node-redis/commit/2d11b6dc9b9774464a91fb4b448bad8bf699629e) and was released in version `3.1.1`.

### References
#1569 (GHSL-2021-026)

## References
- https://github.com/NodeRedis/node-redis/security/advisories/GHSA-35q2-47q7-3pc3
- https://nvd.nist.gov/vuln/detail/CVE-2021-29469
- https://github.com/NodeRedis/node-redis/commit/2d11b6dc9b9774464a91fb4b448bad8bf699629e
- https://github.com/NodeRedis/node-redis/releases/tag/v3.1.1
- https://security.netapp.com/advisory/ntap-20210611-0010
