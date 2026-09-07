# [M] OpenStack Compute (Nova) vulnerable to denial of service via XML Entity Expansion attack

## Summary
Severity: Medium
Advisory: GHSA-j6xh-q826-55jw
CVE: CVE-2013-4179
CWE: CWE-119
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j6xh-q826-55jw
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <2013.2

## Details
The security group extension in OpenStack Compute (Nova) Grizzly 2013.1.3, Havana before havana-3, and earlier allows remote attackers to cause a denial of service (resource consumption and crash) via an XML Entity Expansion (XEE) attack.  NOTE: this issue is due to an incomplete fix for CVE-2013-1664.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4179
- https://access.redhat.com/errata/RHSA-2013:1199
- https://access.redhat.com/security/cve/CVE-2013-4179
- https://bugs.launchpad.net/ossa/+bug/1190229
- https://bugzilla.redhat.com/show_bug.cgi?id=989707
- https://opendev.org/openstack/nova
- http://rhn.redhat.com/errata/RHSA-2013-1199.html
- http://www.ubuntu.com/usn/USN-2005-1
