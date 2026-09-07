# [H] @cubejs-backend/api-gateway row level security bypass

## Summary
Severity: High
Advisory: GHSA-6jqm-3c9g-pch7
CVE: CVE-2022-23510
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-6jqm-3c9g-pch7
Type: github-advisory

## Affected
- npm: `@cubejs-backend/api-gateway` — affected >=0.31.23 <0.31.24

## Details
### Impact
All authenticated Cube clients could bypass row-level security and run arbitrary SQL via the newly introduced /v1/sql-runner endpoint.

### Patches
The change has been reverted in 0.31.24

### Workarounds
Upgrade to >=0.31.24 or downgrade to <=0.31.22

### Post mortem
As part of implementing the Cube Cloud SQL runner functionality, we’ve added a new endpoint to the Cube Core so that we could add arbitrary queries directly to the queue, bypassing the modeling layer.

The endpoint was added in this commit: https://github.com/cube-js/cube.js/commit/f1e25bb50323c0b99f3891d349467e7b637baeea

It went through the code review; however, it slipped everyone’s attention that this endpoint completely bypasses any row-level security logic implemented in the modeling layer. Now anyone with a valid Cube JWT token could fetch any data, even if they were not allowed to do so by their security context.

The issue was noticed by the Core team on Dec 12 and immediately reverted.

The just-released 0.31.23 version of the Cube has been pulled out of all the registries, and a CVE was published on Github.
Another change (https://github.com/cube-js/cube.js/commit/2c5db32f2ded074ebe5e83668eee8c024101240b) was also rolled back along with the SQL runner endpoint. It didn't pose a significant security threat, but it increased the attacker’s ability to enumerate cube schema, and it should be revisited.

The 0.31.24 was released to replace the revoked version with a change completely reverted. All customers are urged to upgrade to the newest Cube version.

## References
- https://github.com/cube-js/cube.js/security/advisories/GHSA-6jqm-3c9g-pch7
- https://nvd.nist.gov/vuln/detail/CVE-2022-23510
- https://github.com/cube-js/cube.js/commit/3c614674fed6ca17df08bbba8c835ef110167570
- https://github.com/cube-js/cube.js/commit/f1140de508e359970ac82b50bae1c4bf152f6041
- https://github.com/cube-js/cube.js
