# [M] OpenStack Image Service (Glance) allows remote authenticated users to bypass access restrictions

## Summary
Severity: Medium
Advisory: GHSA-q748-mcwg-xmqv
CVE: CVE-2015-5251
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q748-mcwg-xmqv
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=2011.2 <2014.2.4
- PyPI: `glance` — affected >=2015.1.0 <2015.1.2

## Details
OpenStack Image Service (Glance) before 2014.2.4 (juno) and 2015.1.x before 2015.1.2 (kilo) allow remote authenticated users to change the status of their images and bypass access restrictions via the HTTP x-image-meta-status header to images/*.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5251
- https://access.redhat.com/errata/RHSA-2015:1897
- https://access.redhat.com/security/cve/CVE-2015-5251
- https://bugs.launchpad.net/bugs/1482371
- https://bugzilla.redhat.com/show_bug.cgi?id=1263511
- https://opendev.org/openstack/glance
- https://rhn.redhat.com/errata/RHSA-2015-1897.html
- https://security.openstack.org/ossa/OSSA-2015-019.html
