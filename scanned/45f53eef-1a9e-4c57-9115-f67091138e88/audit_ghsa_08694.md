# [M] OpenStack Keystone has an Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-2r23-2g6v-2m5f
CVE: CVE-2026-42999
CWE: CWE-639, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-2r23-2g6v-2m5f
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=14.0.0 <27.0.2
- PyPI: `keystone` — affected >=28.0.0 <28.0.2
- PyPI: `keystone` — affected >=29.0.0 <29.0.2

## Details
An issue was discovered in OpenStack Keystone before 29.0.2. The Keystone RBAC policy enforcer in enforce_call unconditionally merges the raw JSON request body into the policy enforcement dictionary via policy_dict.update(json_input.copy()), overwriting trusted target data that was previously set from database lookups. Because flask.request.get_json is called with force=True, this works regardless of Content-Type or HTTP method. Any authenticated user can inject arbitrary policy target attributes (e.g., user_id, project_id) into the request body to bypass RBAC checks and perform unauthorized operations on resources belonging to other users or projects. This was introduced in commit 5ea59f52 (Rocky/14.0.0).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42999
- https://access.redhat.com/security/cve/CVE-2026-42999
- https://bugs.launchpad.net/keystone/+bug/2148398
- https://bugzilla.redhat.com/show_bug.cgi?id=2482840
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2026-600.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42999.json
- https://security.openstack.org/ossa/OSSA-2026-015.html
