# [H] OpenStack Neutron overlapping security group rules prevents compute node network configuration

## Summary
Severity: High
Advisory: GHSA-jr9m-v5qh-mh2j
CVE: CVE-2019-10876
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jr9m-v5qh-mh2j
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=11.0.0 <11.0.7
- PyPI: `neutron` — affected >=12.0.0 <12.0.6
- PyPI: `neutron` — affected >=13.0.0 <13.0.3

## Details
An issue was discovered in OpenStack Neutron 11.x before 11.0.7, 12.x before 12.0.6, and 13.x before 13.0.3. By creating two security groups with separate/overlapping port ranges, an authenticated user may prevent Neutron from being able to configure networks on any compute nodes where those security groups are present, because of an Open vSwitch (OVS) firewall KeyError. All Neutron deployments utilizing neutron-openvswitch-agent are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10876
- https://access.redhat.com/errata/RHSA-2019:0879
- https://access.redhat.com/errata/RHSA-2019:0935
- https://bugs.launchpad.net/ossa/+bug/1813007
- https://github.com/openstack/neutron
- https://github.com/pypa/advisory-database/tree/main/vulns/neutron/PYSEC-2019-189.yaml
- https://review.openstack.org/#/q/topic:bug/1813007
- https://security.openstack.org/ossa/OSSA-2019-002.html
- http://www.openwall.com/lists/oss-security/2019/04/09/2
