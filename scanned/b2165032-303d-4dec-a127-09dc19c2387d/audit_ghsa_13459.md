# [M] Unintentional leakage of private information via cross-origin websocket session hijacking

## Summary
Severity: Medium
Advisory: GHSA-4qcv-qf38-5j3j
CVE: CVE-2023-2850
CWE: CWE-1385, CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-4qcv-qf38-5j3j
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=3.0.0 <3.1.3
- npm: `nodebb` — affected >=0 <2.8.13

## Details
### Impact

Private messages or posts might be leaked to third parties if victim opens the attackers site while browsing nodebb.

### Patches

* Patched in v3.1.3
* Backported to v2.x line via v2.8.13

### Workarounds

Users can cherry-pick https://github.com/NodeBB/NodeBB/commit/51096ad2345fb1d1380bec0a447113489ef6c359 if they are on v3.x

If you are running v2.x of NodeBB, you can cherry-pick a5d92da9ddac5607ab7f737520a66eaed6d3ddee followed by 62e162cf1e735e42462be1db9b4954b5a69accdf

## References
- https://github.com/NodeBB/NodeBB/security/advisories/GHSA-4qcv-qf38-5j3j
- https://nvd.nist.gov/vuln/detail/CVE-2023-2850
- https://github.com/NodeBB/NodeBB/commit/51096ad2345fb1d1380bec0a447113489ef6c359
- https://github.com/NodeBB/NodeBB/commit/62e162cf1e735e42462be1db9b4954b5a69accdf
- https://github.com/NodeBB/NodeBB/commit/a5d92da9ddac5607ab7f737520a66eaed6d3ddee
- https://github.com/NodeBB/NodeBB
- https://github.com/NodeBB/NodeBB/releases/tag/v3.1.3
