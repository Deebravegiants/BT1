# [H] OpenStack Neutron vulnerable to authenticated attackers reconfiguring dnsmasq via crafted extra_dhcp_opts value

## Summary
Severity: High
Advisory: GHSA-fh73-gjvg-349c
CVE: CVE-2021-40085
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fh73-gjvg-349c
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=0 <16.4.1
- PyPI: `neutron` — affected >=17.0.0 <17.2.1
- PyPI: `neutron` — affected >=18.0.0 <18.1.1

## Details
An issue was discovered in OpenStack Neutron before 16.4.1, 17.x before 17.2.1, and 18.x before 18.1.1. Authenticated attackers can reconfigure dnsmasq via a crafted extra_dhcp_opts value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40085
- https://github.com/openstack/neutron/commit/df891f0593d234e01f27d7c0376d9702e178ecfb
- https://github.com/openstack/neutron
- https://github.com/pypa/advisory-database/tree/main/vulns/neutron/PYSEC-2021-361.yaml
- https://launchpad.net/bugs/1939733
- https://lists.debian.org/debian-lts-announce/2021/10/msg00005.html
- https://lists.debian.org/debian-lts-announce/2022/05/msg00038.html
- https://security.openstack.org/ossa/OSSA-2021-005.html
- https://www.debian.org/security/2021/dsa-4983
- http://www.openwall.com/lists/oss-security/2021/08/31/2
