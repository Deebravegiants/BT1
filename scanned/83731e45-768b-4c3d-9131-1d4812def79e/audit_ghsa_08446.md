# [M] OpenStack Cyborg's Accelerator Request (ARQ) API does not enforce project ownership at any layer

## Summary
Severity: Medium
Advisory: GHSA-mmpc-xjxr-5hf8
CVE: CVE-2026-40214
CWE: CWE-282
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-mmpc-xjxr-5hf8
Type: github-advisory

## Affected
- PyPI: `openstack-cyborg` — affected >=0 <16.0.1

## Details
In OpenStack Cyborg before 16.0.1, the Accelerator Request (ARQ) API does not enforce project ownership at any layer. The project_id column in the database is never populated (NULL for every ARQ), database queries have no project filtering, and policy checks are self-referential (the authorize_wsgi decorator compares the caller's project_id with itself rather than the target resource). Any authenticated non-admin user can complete various actions such as deleting ARQs bound to other projects' instances, aka cross-tenant denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40214
- https://bugs.launchpad.net/openstack-cyborg/+bug/2144056
- https://github.com/openstack/cyborg
- https://security.openstack.org/ossa/OSSA-2026-011.html
- https://www.openwall.com/lists/oss-security/2026/05/07/6
