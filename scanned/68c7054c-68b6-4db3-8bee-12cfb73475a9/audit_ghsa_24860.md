# [H] OpenStack Manila Unprivileged users can retrieve, use and manipulate share networks

## Summary
Severity: High
Advisory: GHSA-jx7v-gmqc-6xrj
CVE: CVE-2020-9543
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jx7v-gmqc-6xrj
Type: github-advisory

## Affected
- PyPI: `manila` — affected >=0 <7.4.1
- PyPI: `manila` — affected >=8.0.0 <8.1.1
- PyPI: `manila` — affected >=9.0.0 <9.1.1

## Details
OpenStack Manila <7.4.1, >=8.0.0 <8.1.1, and >=9.0.0 <9.1.1 allows attackers to view, update, delete, or share resources that do not belong to them, because of a context-free lookup of a UUID. Attackers may also create resources, such as shared file systems and groups of shares on such share networks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9543
- https://github.com/openstack/manila/commit/947315f0903c823b0fdd9d99c60078814587272c
- https://bugs.launchpad.net/manila/+bug/1861485
- https://github.com/openstack/manila
- https://github.com/pypa/advisory-database/tree/main/vulns/manila/PYSEC-2020-63.yaml
- https://opendev.org/openstack/manila/commit/947315f0903c823b0fdd9d99c60078814587272c
- https://security.openstack.org/ossa/OSSA-2020-002.html
- http://www.openwall.com/lists/oss-security/2020/03/12/1
