# [C] OpenStack os-vif Ageing time of 0 disables linuxbridge MAC learning

## Summary
Severity: Critical
Advisory: GHSA-mcpw-cp35-p3h8
CVE: CVE-2019-15753
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mcpw-cp35-p3h8
Type: github-advisory

## Affected
- PyPI: `os-vif` — affected >=1.15.0 <1.15.2
- PyPI: `os-vif` — affected >=1.16.0 <1.17.0

## Details
In OpenStack os-vif 1.15.x before 1.15.2, and 1.16.0, a hard-coded MAC aging time of 0 disables MAC learning in linuxbridge, forcing obligatory Ethernet flooding of non-local destinations, which both impedes network performance and allows users to possibly view the content of packets for instances belonging to other tenants sharing the same network. Only deployments using the linuxbridge backend are affected. This occurs in PyRoute2.add() in `internal/command/ip/linux/impl_pyroute2.py`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15753
- https://github.com/openstack/os-vif/commit/655c83d706f5de8a8cf23430782e065219297aef
- https://github.com/openstack/os-vif/commit/ec9d5430300c908ea9a1c64151eee7af522a44e7
- https://github.com/openstack/os-vif
- https://launchpad.net/bugs/1837252
- https://review.opendev.org/672834
- https://review.opendev.org/678098
- https://security.openstack.org/ossa/OSSA-2019-004.html
- http://www.openwall.com/lists/oss-security/2019/08/29/2
