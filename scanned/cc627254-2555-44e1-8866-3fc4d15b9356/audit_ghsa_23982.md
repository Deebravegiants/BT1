# [H] OpenStack Neutron's unsupported dport option prevents applying security groups

## Summary
Severity: High
Advisory: GHSA-9773-3fqg-8w25
CVE: CVE-2019-9735
CWE: CWE-755
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9773-3fqg-8w25
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=0 <10.0.8
- PyPI: `neutron` — affected >=11.0.0 <11.0.7
- PyPI: `neutron` — affected >=12.0.0 <12.0.6
- PyPI: `neutron` — affected >=13.0.0 <13.0.3

## Details
An issue was discovered in the iptables firewall module in OpenStack Neutron before 10.0.8, 11.x before 11.0.7, 12.x before 12.0.6, and 13.x before 13.0.3. By setting a destination port in a security group rule along with a protocol that doesn't support that option (for example, VRRP), an authenticated user may block further application of security group rules for instances from any project/tenant on the compute hosts to which it's applied. (Only deployments using the iptables security group driver are affected.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9735
- https://access.redhat.com/errata/RHSA-2019:0879
- https://access.redhat.com/errata/RHSA-2019:0916
- https://access.redhat.com/errata/RHSA-2019:0935
- https://github.com/openstack/neutron
- https://github.com/pypa/advisory-database/tree/main/vulns/neutron/PYSEC-2019-190.yaml
- https://launchpad.net/bugs/1818385
- https://seclists.org/bugtraq/2019/Mar/24
- https://security.openstack.org/ossa/OSSA-2019-001.html
- https://usn.ubuntu.com/4036-1
- https://web.archive.org/web/20201208185619/http://www.securityfocus.com/bid/107390
- https://www.debian.org/security/2019/dsa-4409
- http://www.openwall.com/lists/oss-security/2019/03/18/2
- http://www.securityfocus.com/bid/107390
