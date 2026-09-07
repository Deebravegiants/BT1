# [M] OpenStack Compute (Nova) allows remote authenticated users to gain privileges via API requests

## Summary
Severity: Medium
Advisory: GHSA-p258-xmh3-72pv
CVE: CVE-2014-0167
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p258-xmh3-72pv
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=2013.1.0 <2013.2.4

## Details
The Nova EC2 API security group implementation in OpenStack Compute (Nova) 2013.1 before 2013.2.4 and icehouse before icehouse-rc2 does not enforce RBAC policies for (1) add_rules, (2) remove_rules, (3) destroy, and other unspecified methods in compute/api.py when using non-default policies, which allows remote authenticated users to gain privileges via these API requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0167
- https://access.redhat.com/errata/RHSA-2014:1084
- https://access.redhat.com/security/cve/CVE-2014-0167
- https://bugzilla.redhat.com/show_bug.cgi?id=1084868
- https://launchpad.net/bugs/1290537
- https://opendev.org/openstack/nova
- http://www.openwall.com/lists/oss-security/2014/04/09/26
- http://www.ubuntu.com/usn/USN-2247-1
