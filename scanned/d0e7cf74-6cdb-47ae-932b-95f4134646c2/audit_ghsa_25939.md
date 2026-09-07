# [M] Open Redirect in CPython that affects users of OpenStack Nova

## Summary
Severity: Medium
Advisory: GHSA-vqp6-j452-j6wp
CVE: CVE-2021-3654
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-vqp6-j452-j6wp
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <21.2.3
- PyPI: `nova` — affected >=22.0.0 <22.2.3
- PyPI: `nova` — affected >=23.0.0 <23.0.3

## Details
A vulnerability was found in CPython which is used by openstack-nova's console proxy, noVNC. By crafting a malicious URL, noVNC could be made to redirect to any desired URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3654
- https://bugs.launchpad.net/nova/+bug/1927677
- https://bugs.python.org/issue32084
- https://bugzilla.redhat.com/show_bug.cgi?id=1961439
- https://opendev.org/openstack/nova
- https://opendev.org/openstack/nova/commit/04d48527b62a35d912f93bc75613a6cca606df66
- https://opendev.org/openstack/nova/commit/8906552cfc2525a44251d4cf313ece61e57251eb
- https://security.gentoo.org/glsa/202305-02
- https://security.openstack.org/ossa/OSSA-2021-002.html
- https://www.openwall.com/lists/oss-security/2021/07/29/2
