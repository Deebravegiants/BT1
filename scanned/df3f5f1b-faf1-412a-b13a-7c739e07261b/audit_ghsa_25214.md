# [H] OpenStack Keystone allows information disclosure during account locking

## Summary
Severity: High
Advisory: GHSA-4225-97pr-rr52
CVE: CVE-2021-38155
CWE: CWE-307
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4225-97pr-rr52
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=10.0 <16.0.2
- PyPI: `keystone` — affected >=17.0 <17.0.1
- PyPI: `keystone` — affected >=18.0 <18.0.1
- PyPI: `keystone` — affected >=19.0 <19.0.1

## Details
OpenStack Keystone 10.x through 16.x before 16.0.2, 17.x before 17.0.1, 18.x before 18.0.1, and 19.x before 19.0.1 allows information disclosure during account locking (related to PCI DSS features). By guessing the name of an account and failing to authenticate multiple times, any unauthenticated actor could both confirm the account exists and obtain that account's corresponding UUID, which might be leveraged for other unrelated attacks. All deployments enabling security_compliance.lockout_failure_attempts are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38155
- https://github.com/openstack/keystone/commit/1b573ae7d1c20e0ebfbde79bbe7538a09589c75d
- https://github.com/openstack/keystone/commit/8ab4eb27be4c13c9bab2b3ea700f00a190521bf8
- https://github.com/openstack/keystone/commit/ac2631ae33445877094cdae796fbcdce8833a626
- https://github.com/openstack/keystone
- https://launchpad.net/bugs/1688137
- https://lists.debian.org/debian-lts-announce/2024/01/msg00007.html
- https://security.openstack.org/ossa/OSSA-2021-003.html
- http://www.openwall.com/lists/oss-security/2021/08/10/5
