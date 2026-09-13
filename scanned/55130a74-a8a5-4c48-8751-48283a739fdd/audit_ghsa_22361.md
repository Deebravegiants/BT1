# [H] Openstack Neutron has Insufficient Verification of IPv6 addresses

## Summary
Severity: High
Advisory: GHSA-w8hx-f868-pvch
CVE: CVE-2021-20267
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w8hx-f868-pvch
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=16.0.0 <16.3.1
- PyPI: `neutron` — affected >=0 <15.3.3
- PyPI: `neutron` — affected >=17.0.0 <17.1.1

## Details
A flaw was found in openstack-neutron's default Open vSwitch firewall rules. By sending carefully crafted packets, anyone in control of a server instance connected to the virtual switch can impersonate the IPv6 addresses of other systems on the network, resulting in denial of service or in some cases possibly interception of traffic intended for other destinations. Only deployments using the Open vSwitch driver are affected. Source: OpenStack project. Versions before openstack-neutron 15.3.3, openstack-neutron 16.3.1 and openstack-neutron 17.1.1 are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20267
- https://bugzilla.redhat.com/show_bug.cgi?id=1934330
- https://github.com/openstack/neutron
- https://github.com/pypa/advisory-database/tree/main/vulns/neutron/PYSEC-2021-136.yaml
- https://security.openstack.org/ossa/OSSA-2021-001.html
