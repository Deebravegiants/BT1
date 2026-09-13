# [C] OpenStack Vitrage: Unauthorized Access to the Host can Lead to Eval Injection

## Summary
Severity: Critical
Advisory: GHSA-8xwf-cr4r-856r
CVE: CVE-2026-28370
CWE: CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-8xwf-cr4r-856r
Type: github-advisory

## Affected
- PyPI: `vitrage` — affected >=15.0.0.0rc1 <15.0.1
- PyPI: `vitrage` — affected >=14.0.0.0rc1 <14.0.1
- PyPI: `vitrage` — affected >=13.0.0.0rc1 <13.0.1
- PyPI: `vitrage` — affected >=0 <12.0.1

## Details
In the query parser in OpenStack Vitrage before 12.0.1, 13.0.0, 14.0.0, and 15.0.0, a user allowed to access the Vitrage API may trigger code execution on the Vitrage service host as the user the Vitrage service runs under. This may result in unauthorized access to the host and further compromise of the Vitrage service. All deployments exposing the Vitrage API are affected. This occurs in _create_query_function in vitrage/graph/query.py.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28370
- https://github.com/openstack/vitrage/commit/89df4bd2ffda1a5ddea66cd828438a6a171a3b11
- https://github.com/openstack/vitrage
- https://github.com/openstack/vitrage/blob/a1f86950e1314b0c740f9cd9b7e9dbab7d02af51/vitrage/graph/query.py#L70
- https://storyboard.openstack.org/#%21/story/2011539
- http://www.openwall.com/lists/oss-security/2026/03/03/6
