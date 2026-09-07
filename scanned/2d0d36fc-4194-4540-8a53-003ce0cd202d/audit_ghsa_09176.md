# [M] OpenStack Horizon has Incorrect Behavior Order

## Summary
Severity: Medium
Advisory: GHSA-vxvf-xvm3-p8j5
CVE: CVE-2026-43002
CWE: CWE-696
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-vxvf-xvm3-p8j5
Type: github-advisory

## Affected
- PyPI: `horizon` — affected >=25.6 <25.7.3

## Details
An issue was discovered in OpenStack Horizon 25.6 and 25.7 before 25.7.3. There is a write operation to the session storage backend before authentication and thus storage can be exhausted by unauthenticated requests. This is a regression of the CVE-2014-8124 fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43002
- https://bugs.launchpad.net/horizon/+bug/2150331
- https://github.com/openstack/horizon
- https://security.openstack.org/ossa/OSSA-2026-009.html
- https://www.openwall.com/lists/oss-security/2026/05/05/7
