# [M] OpenStack Nova Directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m454-cm7h-rqhh
CVE: CVE-2012-3360
CWE: CWE-22
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m454-cm7h-rqhh
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
Directory traversal vulnerability in `virt/disk/api.py` in OpenStack Compute (Nova) Folsom (2012.2) and Essex (2012.1), when used over libvirt-based hypervisors, allows remote authenticated users to write arbitrary files to the disk image via a .. (dot dot) in the path attribute of a file element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3360
- https://github.com/openstack/nova/commit/2427d4a99bed35baefd8f17ba422cb7aae8dcca7
- https://github.com/openstack/nova/commit/b0feaffdb2b1c51182b8dce41b367f3449af5dd9
- https://bugs.launchpad.net/nova/+bug/1015531
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2012-38.yaml
- https://lists.launchpad.net/openstack/msg14089.html
- http://www.ubuntu.com/usn/USN-1497-1
