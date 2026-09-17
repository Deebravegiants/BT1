# [M] OpenStack Keystone does not invalidate existing tokens when granting or revoking roles

## Summary
Severity: Medium
Advisory: GHSA-mrxv-65rv-6hxq
CVE: CVE-2012-4413
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-mrxv-65rv-6hxq
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <2012.1.3

## Details
OpenStack Keystone before 2012.1.3 does not invalidate existing tokens when granting or revoking roles, which allows remote authenticated users to retain the privileges of the revoked roles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4413
- https://access.redhat.com/errata/RHSA-2012:1378
- https://access.redhat.com/security/cve/CVE-2012-4413
- https://bugs.launchpad.net/keystone/+bug/1041396
- https://bugzilla.redhat.com/show_bug.cgi?id=855491
- https://exchange.xforce.ibmcloud.com/vulnerabilities/78478
- https://opendev.org/openstack/keystone
- https://review.opendev.org/c/openstack/keystone/+/12870
- https://web.archive.org/web/20121114023848/http://www.securityfocus.com/bid/55524
- http://github.com/openstack/keystone/commit/58ac6691a21675be9e2ffb0f84a05fc3cd4d2e2e
- http://www.openwall.com/lists/oss-security/2012/09/12/7
- http://www.ubuntu.com/usn/USN-1564-1
