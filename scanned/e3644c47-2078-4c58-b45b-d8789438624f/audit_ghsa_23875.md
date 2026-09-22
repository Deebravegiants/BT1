# [H] OpenStack Keystone EC2 and/or credential endpoints are not protected from a scoped context 

## Summary
Severity: High
Advisory: GHSA-chgw-36xv-47cw
CVE: CVE-2020-12689
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-chgw-36xv-47cw
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <15.0.1
- PyPI: `keystone` — affected >=16.0.0 <16.0.1

## Details
An issue was discovered in OpenStack Keystone before 15.0.1, and 16.0.0. Any user authenticated within a limited scope (trust/oauth/application credential) can create an EC2 credential with an escalated permission, such as obtaining admin while the user is on a limited viewer role. This potentially allows a malicious user to act as the admin on a project another user has the admin role on, which can effectively grant that user global admin privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12689
- https://github.com/openstack/keystone/commit/37e9907a176dad6843819b1bec4946c3aecc4548
- https://bugs.launchpad.net/keystone/+bug/1872735
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2020-53.yaml
- https://lists.apache.org/thread.html/re4ffc55cd2f1b55a26e07c83b3c22c3fe4bae6054d000a57fb48d8c2@%3Ccommits.druid.apache.org%3E
- https://security.openstack.org/ossa/OSSA-2020-004.html
- https://usn.ubuntu.com/4480-1
- https://www.openwall.com/lists/oss-security/2020/05/06/5
- http://www.openwall.com/lists/oss-security/2020/05/07/2
