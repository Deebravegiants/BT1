# [M] Moodle vulnerable to SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-49mv-vfcp-8gg9
CVE: CVE-2023-35132
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-49mv-vfcp-8gg9
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.2.0 <4.2.1
- Packagist: `moodle/moodle` — affected >=4.1.0 <4.1.4
- Packagist: `moodle/moodle` — affected >=4.0.0 <4.0.9
- Packagist: `moodle/moodle` — affected >=3.10.0 <3.11.15
- Packagist: `moodle/moodle` — affected >=0 <3.9.22

## Details
A limited SQL injection risk was identified on the Mnet SSO access control page. This flaw affects Moodle versions 4.2, 4.1 to 4.1.3, 4.0 to 4.0.8, 3.11 to 3.11.14, 3.9 to 3.9.21 and earlier unsupported versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35132
- https://bugzilla.redhat.com/show_bug.cgi?id=2214371
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7A72KX4WU6GK2CX4TKYFGFASPKOEOJFC
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I5QAEAGJ44NVXLAJFJXKARKC45OGEDXT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7A72KX4WU6GK2CX4TKYFGFASPKOEOJFC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I5QAEAGJ44NVXLAJFJXKARKC45OGEDXT
- https://moodle.org/mod/forum/discuss.php?d=447830
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-77193
