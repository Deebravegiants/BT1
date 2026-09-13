# [M] OpenStack Cinder file disclosure in image convert

## Summary
Severity: Medium
Advisory: GHSA-9hcj-h2qc-689p
CVE: CVE-2015-1851
CWE: CWE-200
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9hcj-h2qc-689p
Type: github-advisory

## Affected
- PyPI: `cinder` — affected >=0 <7.0.0a0

## Details
OpenStack Cinder before 2014.1.5 (icehouse), 2014.2.x before 2014.2.4 (juno), and 2015.1.x before 2015.1.1 (kilo) allows remote authenticated users to read arbitrary files via a crafted qcow2 signature in an image to the upload-to-image command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1851
- https://github.com/openstack/cinder/commit/9634b76ba5886d6c2f2128d550cb005dabf48213
- https://github.com/openstack/cinder/commit/b1143ee45323e63b965a3710f9063e65b252c978
- https://github.com/openstack/cinder/commit/bc0549e08b010edb863d409d80114aa78d317a61
- https://github.com/openstack/cinder/commit/d31c937c566005dedf41a60c6b5bd5e7b26f221b
- https://bugs.launchpad.net/cinder/+bug/1415087
- https://github.com/openstack/cinder
- http://lists.openstack.org/pipermail/openstack-announce/2015-June/000367.html
- http://rhn.redhat.com/errata/RHSA-2015-1206.html
- http://www.debian.org/security/2015/dsa-3292
- http://www.openwall.com/lists/oss-security/2015/06/13/1
- http://www.openwall.com/lists/oss-security/2015/06/17/2
- http://www.openwall.com/lists/oss-security/2015/06/17/7
- http://www.ubuntu.com/usn/USN-2703-1
