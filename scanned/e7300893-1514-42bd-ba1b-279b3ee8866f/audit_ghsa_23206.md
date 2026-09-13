# [H] Ansible Sandbox Escape via Symlink Attack

## Summary
Severity: High
Advisory: GHSA-wwwh-47wp-m522
CVE: CVE-2015-6240
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wwwh-47wp-m522
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <1.9.2

## Details
The chroot, jail, and zone connection plugins in ansible before 1.9.2 allow local users to escape a restricted environment via a symlink attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-6240
- https://github.com/ansible/ansible/commit/952166f48eb0f5797b75b160fd156bbe1e8fc647
- https://github.com/ansible/ansible/commit/ca2f2c4ebd7b5e097eab0a710f79c1f63badf95b
- https://bugzilla.redhat.com/show_bug.cgi?id=1243468
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2017-3.yaml
- https://lists.debian.org/debian-lts-announce/2019/09/msg00016.html
- http://www.openwall.com/lists/oss-security/2015/08/17/10
