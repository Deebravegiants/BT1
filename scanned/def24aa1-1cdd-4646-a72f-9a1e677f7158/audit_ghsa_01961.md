# [H] Insufficient Session Expiration in OpenStack Keystone

## Summary
Severity: High
Advisory: GHSA-6m8p-x4qw-gh5j
CVE: CVE-2020-12690
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-09
Source: https://github.com/advisories/GHSA-6m8p-x4qw-gh5j
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <15.0.1
- PyPI: `keystone` — affected >=16.0.0.0rc1 <16.0.0

## Details
An issue was discovered in OpenStack Keystone before 15.0.1, and 16.0.0. The list of roles provided for an OAuth1 access token is silently ignored. Thus, when an access token is used to request a keystone token, the keystone token contains every role assignment the creator had for the project. This results in the provided keystone token having more role assignments than the creator intended, possibly giving unintended escalated access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12690
- https://bugs.launchpad.net/keystone/+bug/1873290
- https://github.com/advisories/GHSA-6m8p-x4qw-gh5j
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2020-54.yaml
- https://lists.apache.org/thread.html/re4ffc55cd2f1b55a26e07c83b3c22c3fe4bae6054d000a57fb48d8c2@%3Ccommits.druid.apache.org%3E
- https://security.openstack.org/ossa/OSSA-2020-005.html
- https://usn.ubuntu.com/4480-1
- https://www.openwall.com/lists/oss-security/2020/05/06/6
- http://www.openwall.com/lists/oss-security/2020/05/07/3
