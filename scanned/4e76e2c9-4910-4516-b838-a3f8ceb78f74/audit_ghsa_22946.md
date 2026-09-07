# [M] OpenStack Glance Bypass the storage quota and Denial of service 

## Summary
Severity: Medium
Advisory: GHSA-j4mh-9wq6-8rg6
CVE: CVE-2014-9623
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j4mh-9wq6-8rg6
Type: github-advisory

## Affected
- PyPI: `glance` — affected >=0 <11.0.0a0

## Details
OpenStack Glance 2014.2.x through 2014.2.1, 2014.1.3, and earlier allows remote authenticated users to bypass the storage quota and cause a denial of service (disk consumption) by deleting an image in the saving state.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9623
- https://github.com/openstack/glance/commit/0dc8fbb3479a53c5bba8475d14f4c7206904c5ea
- https://github.com/openstack/glance/commit/7d5d8657fd70b20518610b3c6f8e41e16c72fa31
- https://github.com/openstack/glance/commit/f1260cc771ee068651aa62b972bef49d9af81eb0
- https://bugs.launchpad.net/glance/+bug/1383973
- https://bugs.launchpad.net/glance/+bug/1398830
- https://github.com/openstack/glance
- https://security.openstack.org/ossa/OSSA-2015-003.html
- http://rhn.redhat.com/errata/RHSA-2015-0644.html
- http://rhn.redhat.com/errata/RHSA-2015-0837.html
- http://rhn.redhat.com/errata/RHSA-2015-0838.html
- http://secunia.com/advisories/62165
- http://www.openwall.com/lists/oss-security/2015/01/18/4
- http://www.oracle.com/technetwork/topics/security/bulletinapr2015-2511959.html
