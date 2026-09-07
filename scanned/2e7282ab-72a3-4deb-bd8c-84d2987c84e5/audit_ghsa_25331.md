# [M] OpenStack Nova Information leak in libvirt LVM-backed instances

## Summary
Severity: Medium
Advisory: GHSA-rwhr-h69g-8qmq
CVE: CVE-2012-5625
CWE: CWE-200
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rwhr-h69g-8qmq
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
OpenStack Compute (Nova) Folsom before 2012.2.2 and Grizzly, when using libvirt and LVM backed instances, does not properly clear physical volume (PV) content when reallocating for instances, which allows attackers to obtain sensitive information by reading the memory of the previous logical volume (LV).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5625
- https://github.com/openstack/nova/commit/9d2ea970422591f8cdc394001be9a2deca499a5f
- https://github.com/openstack/nova/commit/a99a802e008eed18e39fc1d98170edc495cbd354
- https://bugs.launchpad.net/nova/+bug/1070539
- https://bugzilla.redhat.com/show_bug.cgi?id=884293
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2012-41.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2012-42.yaml
- https://launchpad.net/nova/folsom/2012.2.2
- http://rhn.redhat.com/errata/RHSA-2013-0208.html
- http://www.openwall.com/lists/oss-security/2012/12/11/5
- http://www.ubuntu.com/usn/USN-1663-1
