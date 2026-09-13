# [M] OpenStack Nova DoS through ephemeral disk backing files

## Summary
Severity: Medium
Advisory: GHSA-hrv9-4x4c-9jc8
CVE: CVE-2013-6437
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-hrv9-4x4c-9jc8
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
The libvirt driver in OpenStack Compute (Nova) before 2013.2.2 and icehouse before icehouse-2 allows remote authenticated users to cause a denial of service (disk consumption) by creating and deleting instances with unique os_type settings, which triggers the creation of a new ephemeral disk backing file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6437
- https://github.com/openstack/nova/commit/3e451f1bac57d24e47171cffb3ad59bb1610d836
- https://github.com/openstack/nova/commit/6e455cd97f04bf26bbe022be17c57e089cf502f4
- https://github.com/openstack/nova/commit/ca38774ebcf5b67d16c202c8f218c0c433973ca9
- https://bugs.launchpad.net/nova/+bug/1253980
- https://github.com/openstack/nova
- http://lists.openstack.org/pipermail/openstack-announce/2013-December/000179.html
- http://rhn.redhat.com/errata/RHSA-2014-0231.html
