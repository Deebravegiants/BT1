# [H] OpenStack Nova-LXD bypass security restrictions

## Summary
Severity: High
Advisory: GHSA-6xc7-4cx8-j3xc
CVE: CVE-2017-5936
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6xc7-4cx8-j3xc
Type: github-advisory

## Affected
- PyPI: `nova-lxd` — affected >=0 <13.1.1

## Details
OpenStack Nova-LXD before 13.1.1 uses the wrong name for the veth pairs when applying Neutron security group rules for instances, which allows remote attackers to bypass intended security restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5936
- https://github.com/openstack/nova-lxd/commit/1b76cefb92081efa1e88cd8f330253f857028bd2
- https://bugs.launchpad.net/nova-lxd/+bug/1656847
- https://github.com/openstack/nova-lxd
- https://github.com/pypa/advisory-database/tree/main/vulns/nova-lxd/PYSEC-2017-21.yaml
- https://web.archive.org/web/20200227193915/http://www.securityfocus.com/bid/96182
- http://www.openwall.com/lists/oss-security/2017/02/09/3
- http://www.ubuntu.com/usn/USN-3195-1
