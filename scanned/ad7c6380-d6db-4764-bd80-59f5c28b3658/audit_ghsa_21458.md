# [M] NodeBB vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-5gwx-wf9g-r5mx
CVE: CVE-2022-3978
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-13
Source: https://github.com/advisories/GHSA-5gwx-wf9g-r5mx
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=0 <2.5.8

## Details
A vulnerability was found in NodeBB up to 2.5.7. This affects an unknown part of the file /register/abort. The manipulation leads to cross-site request forgery. It is possible to initiate the attack remotely. Upgrading to version 2.5.8 is able to address this issue. The name of the patch is 2f9d8c350e54543f608d3d4c8e1a49bbb6cdea38. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3978
- https://github.com/NodeBB/NodeBB/issues/11017
- https://github.com/NodeBB/NodeBB/commit/2f9d8c350e54543f608d3d4c8e1a49bbb6cdea38
- https://github.com/NodeBB/NodeBB/releases/tag/v2.5.8
- https://vuldb.com/?id.213555
