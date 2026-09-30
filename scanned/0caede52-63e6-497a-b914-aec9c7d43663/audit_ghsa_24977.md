# [H] OpenStack Neutron vulnerable to hardware address impersonation

## Summary
Severity: High
Advisory: GHSA-hvm4-mc7m-22w4
CVE: CVE-2021-38598
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hvm4-mc7m-22w4
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=0 <16.4.1
- PyPI: `neutron` — affected >=17.0.0 <17.1.3
- PyPI: `neutron` — affected 18.0.0

## Details
OpenStack Neutron before 16.4.1, 17.x before 17.1.3, and 18.0.0 allows hardware address impersonation when the linuxbridge driver with ebtables-nft is used on a Netfilter-based platform. By sending carefully crafted packets, anyone in control of a server instance connected to the virtual switch can impersonate the hardware addresses of other systems on the network, resulting in denial of service or in some cases possibly interception of traffic intended for other destinations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38598
- https://github.com/openstack/neutron/commit/0a931391d8990f3e654b4bfda24ae4119c609bbf
- https://github.com/openstack/neutron/commit/cc0d28a3e2ccfad6fc2ff24d78f009cbe3992575
- https://github.com/openstack/neutron
- https://github.com/pypa/advisory-database/tree/main/vulns/neutron/PYSEC-2021-360.yaml
- https://launchpad.net/bugs/1938670
- https://opendev.org/openstack/neutron/commit/fafa5dacd5057120562184a734e7345e7c0e9639
