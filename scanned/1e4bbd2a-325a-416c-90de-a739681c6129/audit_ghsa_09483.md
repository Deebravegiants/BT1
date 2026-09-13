# [H] OpenStack Cyborg uses rule:allow (check_str='@') as the default policy for multiple API endpoints

## Summary
Severity: High
Advisory: GHSA-mm7j-mhhj-hj36
CVE: CVE-2026-40213
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-mm7j-mhhj-hj36
Type: github-advisory

## Affected
- PyPI: `openstack-cyborg` — affected >=0 <16.0.1

## Details
OpenStack Cyborg before 16.0.1 uses rule:allow (check_str='@') as the default policy for multiple API endpoints. This unconditionally authorizes any request carrying a valid Keystone token regardless of roles, project membership, or scope. An authenticated user with zero role assignments can complete various actions such as reprogramming FPGA bitstreams on arbitrary compute nodes via agent RPC.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40213
- https://bugs.launchpad.net/openstack-cyborg/+bug/2143263
- https://github.com/openstack/cyborg
- https://security.openstack.org/ossa/OSSA-2026-011.html
- https://www.openwall.com/lists/oss-security/2026/05/07/6
