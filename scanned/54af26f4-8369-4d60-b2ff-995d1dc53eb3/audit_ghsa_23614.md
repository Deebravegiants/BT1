# [H] OpenStack Compute Nova Unauthorised access to arbitrary VM using VNC token from deleted VM

## Summary
Severity: High
Advisory: GHSA-qfp8-hfqx-c79c
CVE: CVE-2013-0335
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-qfp8-hfqx-c79c
Type: github-advisory

## Affected
- PyPI: `Nova` — affected >=0 <12.0.0a0

## Details
OpenStack Compute (Nova) Grizzly, Folsom (2012.2), and Essex (2012.1) allows remote authenticated users to gain access to a VM in opportunistic circumstances by using the VNC token for a deleted VM that was bound to the same VNC port.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0335
- https://bugs.launchpad.net/nova/+bug/1125378
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2013-43.yaml
- https://review.openstack.org/#/c/22086
- https://review.openstack.org/#/c/22758
- https://review.openstack.org/#/c/22872
- http://github.com/openstack/nova/commit/05a3374992bc8ba53ddc9c491b51c4b59eed0a72
- http://github.com/openstack/nova/commit/3b0f4cf6bea33e6ee1893f6e872d968b0c309f88
- http://github.com/openstack/nova/commit/48e81f1554ce41c3d4f7445421d19f4a8128e98d
- http://github.com/openstack/nova/commit/ad94a90202193335f011888db017e557b07faf8a
- http://github.com/openstack/nova/commit/e98928cf77645fdc309da894f3bd332e99482e0d
- http://rhn.redhat.com/errata/RHSA-2013-0709.html
- http://www.openwall.com/lists/oss-security/2013/02/26/7
- http://www.ubuntu.com/usn/USN-1771-1
