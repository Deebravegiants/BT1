# [M] CVE-2026-76878

## Summary
Severity: Medium
Advisory: CVE-2026-76878
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:H/SA:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76878
Type: osv

## Details
In OpenStack Aodh before 22.0.1, the alarm list API bypasses project scoping when the all_projects query parameter is set to false. The API checks for the presence of the all_projects key rather than its value; a true value enforces the administrator-only policy, but a false value removes the key and skips the branch that normally restricts results to the caller's project. A non-admin user with the reader role can list alarms from all projects, exposing alarm actions containing trust webhook URLs, Heat signal endpoints, project IDs, and user IDs. The parameter can also be combined with a foreign project_id to target a specific project's alarms. A related concern is that OpenStack Watcher does not apply authorization to its webhook trigger endpoint. Any authenticated user who learns an audit's webhook URL, for example from this leaked Aodh alarm metadata, can start an EVENT audit and its associated action plan regardless of their own project or role. The webhook endpoint has lacked policy enforcement since its introduction in the Ussuri release (Watcher 4.0.0).

## References
- http://www.openwall.com/lists/oss-security/2026/08/20/21
- https://opendev.org/openstack/aodh
- https://www.openwall.com/lists/oss-security/2026/08/19/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76878.json
- https://lists.openstack.org/archives/list/openstack-announce@lists.openstack.org/thread/O6PKAUNMNZP6FRHLUUGBYELCRBEPB52B/
- https://nvd.nist.gov/vuln/detail/CVE-2026-76878
- https://security.openstack.org/ossa/OSSA-2026-036.html
- https://launchpad.net/bugs/2161276
- https://launchpad.net/bugs/2161771
