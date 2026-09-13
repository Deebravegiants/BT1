# [C] Openstack Keystone Incorrect Authorization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-cc99-whm5-mmq3
CVE: CVE-2021-3563
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-08-27
Source: https://github.com/advisories/GHSA-cc99-whm5-mmq3
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0

## Details
A flaw was found in openstack-keystone, only the first 72 characters of an application secret are verified allowing attackers bypass some password complexity which administrators may be counting on. The highest threat from this vulnerability is to data confidentiality and integrity. A [patch](https://opendev.org/openstack/keystone/commit/7859ed26003858ebfd9a5e866b43f1a6a9e83dca) is available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3563
- https://access.redhat.com/security/cve/CVE-2021-3563
- https://bugs.launchpad.net/ossa/+bug/1901891
- https://bugzilla.redhat.com/show_bug.cgi?id=1962908
- https://lists.debian.org/debian-lts-announce/2024/01/msg00007.html
- https://opendev.org/openstack/keystone
- https://opendev.org/openstack/keystone/commit/7859ed26003858ebfd9a5e866b43f1a6a9e83dca
- https://review.opendev.org/c/openstack/keystone/+/803641
- https://review.opendev.org/c/openstack/keystone/+/828595
- https://review.opendev.org/c/openstack/keystone/+/856489
- https://security-tracker.debian.org/tracker/CVE-2021-3563
