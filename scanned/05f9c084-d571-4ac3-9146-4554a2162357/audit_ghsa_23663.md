# [M] OpenStack Keystone does not check signature TTL of the EC2 credential auth method

## Summary
Severity: Medium
Advisory: GHSA-rqw2-hhrf-7936
CVE: CVE-2020-12692
CWE: CWE-311, CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rqw2-hhrf-7936
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=16.0.0.0rc1 <16.0.0
- PyPI: `keystone` — affected >=0 <15.0.1

## Details
An issue was discovered in OpenStack Keystone before 15.0.1, and 16.0.0. The EC2 API doesn't have a signature TTL check for AWS Signature V4. An attacker can sniff the Authorization header, and then use it to reissue an OpenStack token an unlimited number of times.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12692
- https://bugs.launchpad.net/keystone/+bug/1872737
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2020-56.yaml
- https://opendev.org/openstack/keystone/commit/ab89ea749013e7f2c46260f68504f5687763e019
- https://security.openstack.org/ossa/OSSA-2020-003.html
- https://usn.ubuntu.com/4480-1
- https://www.openwall.com/lists/oss-security/2020/05/06/4
- http://www.openwall.com/lists/oss-security/2020/05/07/1
