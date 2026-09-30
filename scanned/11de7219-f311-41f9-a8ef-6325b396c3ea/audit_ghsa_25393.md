# [H] OpenStack Neutron Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-cpx3-696p-3cw9
CVE: CVE-2021-40797
CWE: CWE-772
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cpx3-696p-3cw9
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=0 <16.4.1
- PyPI: `neutron` — affected >=17.0.0 <17.2.1
- PyPI: `neutron` — affected >=18.0.0 <18.1.1

## Details
An issue was discovered in the routes middleware in OpenStack Neutron before 16.4.1, 17.x before 17.2.1, and 18.x before 18.1.1. By making API requests involving nonexistent controllers, an authenticated user may cause the API worker to consume increasing amounts of memory, resulting in API performance degradation or denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40797
- https://github.com/openstack/neutron/commit/e610a5eb9e71aa2549fb11e2139370d227787da2
- https://github.com/openstack/neutron
- https://github.com/pypa/advisory-database/tree/main/vulns/neutron/PYSEC-2021-329.yaml
- https://launchpad.net/bugs/1942179
- https://security.openstack.org/ossa/OSSA-2021-006.html
- http://www.openwall.com/lists/oss-security/2021/09/09/2
