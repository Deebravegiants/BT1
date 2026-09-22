# [M] OpenStack Neutron Improper Authentication vulnerability

## Summary
Severity: Medium
Advisory: GHSA-72p9-6gc7-q93r
CVE: CVE-2014-0056
CWE: CWE-287
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-72p9-6gc7-q93r
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=2012.2 <2013.2.3

## Details
The l3-agent in OpenStack Neutron 2012.2 before 2013.2.3 does not check the tenant id when creating ports, which allows remote authenticated users to plug ports into the routers of arbitrary tenants via the device id in a port-create command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0056
- https://access.redhat.com/errata/RHSA-2014:0516
- https://access.redhat.com/security/cve/CVE-2014-0056
- https://bugs.launchpad.net/neutron/+bug/1243327
- https://bugzilla.redhat.com/show_bug.cgi?id=1063141
- https://opendev.org/openstack/neutron
- http://rhn.redhat.com/errata/RHSA-2014-0516.html
- http://www.openwall.com/lists/oss-security/2014/03/27/5
- http://www.ubuntu.com/usn/USN-2194-1
