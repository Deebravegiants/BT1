# [M] OpenStack Nova VMware instance leak potentially leading to compute DoS

## Summary
Severity: Medium
Advisory: GHSA-g63p-mfcm-54c4
CVE: CVE-2014-8333
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g63p-mfcm-54c4
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
The VMware driver in OpenStack Compute (Nova) before 2014.1.4 allows remote authenticated users to cause a denial of service (disk consumption) by deleting an instance in the resize state.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8333
- https://github.com/openstack/nova/commit/d71445c7d2d2921d10a08f82330f0ab8ef4f7df2
- https://github.com/openstack/nova/commit/e1f8664c9fa83f77f5bb763ffcc3157905ed954c
- https://bugs.launchpad.net/nova/+bug/1359138
- https://github.com/openstack/nova
- http://lists.openstack.org/pipermail/openstack-announce/2014-October/000298.html
- http://rhn.redhat.com/errata/RHSA-2015-0843.html
- http://rhn.redhat.com/errata/RHSA-2015-0844.html
- http://secunia.com/advisories/60531
