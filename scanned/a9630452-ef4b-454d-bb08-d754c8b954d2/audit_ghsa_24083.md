# [M] OpenStack Image Registry and Delivery Service (Glance) Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r7pj-rvwg-vxhr
CVE: CVE-2014-0162
CWE: CWE-20
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r7pj-rvwg-vxhr
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=2013.2 <2013.2.4

## Details
The Sheepdog backend in OpenStack Image Registry and Delivery Service (Glance) 2013.2 before 2013.2.4 and icehouse before icehouse-rc2 allows remote authenticated users with permission to insert or modify an image to execute arbitrary commands via a crafted location.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0162
- https://access.redhat.com/errata/RHSA-2014:0455
- https://access.redhat.com/security/cve/CVE-2014-0162
- https://bugzilla.redhat.com/show_bug.cgi?id=1085163
- https://launchpad.net/bugs/1298698
- https://opendev.org/openstack/glance
- http://rhn.redhat.com/errata/RHSA-2014-0455.html
- http://www.openwall.com/lists/oss-security/2014/04/10/13
- http://www.ubuntu.com/usn/USN-2193-1
