# [M] OpenStack Compute (Nova) Exposure of Sensitive Information to an Unauthorized Actor vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xjmj-p278-4jp5
CVE: CVE-2014-3517
CWE: CWE-200
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xjmj-p278-4jp5
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <2013.2.4
- PyPI: `nova` — affected >=2014.0.0 <2014.1.2

## Details
api/metadata/handler.py in OpenStack Compute (Nova) before 2013.2.4, 2014.x before 2014.1.2, and Juno before Juno-2, when proxying metadata requests through Neutron, makes it easier for remote attackers to guess instance ID signatures via a brute-force attack that relies on timing differences in responses to instance metadata requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3517
- https://access.redhat.com/errata/RHSA-2014:0940
- https://access.redhat.com/errata/RHSA-2014:1084
- https://access.redhat.com/security/cve/CVE-2014-3517
- https://bugs.launchpad.net/nova/+bug/1325128
- https://bugzilla.redhat.com/show_bug.cgi?id=1112499
- https://opendev.org/openstack/nova
- http://www.openwall.com/lists/oss-security/2014/07/17/2
