# [M] OpenStack Keystone Token authorization for a user in a disabled tenant is allowed

## Summary
Severity: Medium
Advisory: GHSA-x8h4-xf47-pqc3
CVE: CVE-2012-4457
CWE: CWE-287
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x8h4-xf47-pqc3
Type: github-advisory

## Affected
- PyPI: `Keystone` — affected >=0 <8.0.0a0

## Details
OpenStack Keystone Essex before 2012.1.2 and Folsom before folsom-3 does not properly handle authorization tokens for disabled tenants, which allows remote authenticated users to access the tenant's resources by requesting a token for the tenant.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4457
- https://github.com/openstack/keystone/commit/4ebfdfaf23c6da8e3c182bf3ec2cb2b7132ef685
- https://github.com/openstack/keystone/commit/5373601bbdda10f879c08af1698852142b75f8d5
- https://bugzilla.redhat.com/show_bug.cgi?id=861180
- https://exchange.xforce.ibmcloud.com/vulnerabilities/78947
- https://github.com/openstack/keystone
- https://lists.launchpad.net/openstack/msg17035.html
- http://secunia.com/advisories/50665
- http://www.openwall.com/lists/oss-security/2012/09/28/6
- http://www.securityfocus.com/bid/55716
