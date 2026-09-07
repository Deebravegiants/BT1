# [M] lxml NULL Pointer Dereference allows attackers to cause a denial of service

## Summary
Severity: Medium
Advisory: GHSA-wrxv-2j5q-m38w
CVE: CVE-2022-2309
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-07-06
Source: https://github.com/advisories/GHSA-wrxv-2j5q-m38w
Type: github-advisory

## Affected
- PyPI: `lxml` — affected >=0 <4.9.1

## Details
NULL Pointer Dereference allows attackers to cause a denial of service (or application crash). This only applies when lxml is used together with libxml2 2.9.10 through 2.9.14. libxml2 2.9.9 and earlier are not affected. It allows triggering crashes through forged input data, given a vulnerable code sequence in the application. The vulnerability is caused by the iterwalk function (also used by the canonicalize function). Such code shouldn't be in wide-spread use, given that parsing + iterwalk would usually be replaced with the more efficient iterparse function. However, an XML converter that serialises to C14N would also be vulnerable, for example, and there are legitimate use cases for this code sequence. If untrusted input is received (also remotely) and processed via iterwalk function, a crash can be triggered.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2309
- https://github.com/lxml/lxml/commit/86368e9cf70a0ad23cccd5ee32de847149af0c6f
- https://github.com/advisories/GHSA-wrxv-2j5q-m38w
- https://github.com/lxml/lxml
- https://github.com/lxml/lxml/blob/master/CHANGES.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/lxml/PYSEC-2022-230.yaml
- https://huntr.dev/bounties/8264e74f-edda-4c40-9956-49de635105ba
- https://lists.debian.org/debian-lts-announce/2024/09/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HGYC6L7ENH5VEGN3YWFBYMGKX6WNS7HZ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/URHHSIBTPTALXMECRLAC2EVDNAFSR5NO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HGYC6L7ENH5VEGN3YWFBYMGKX6WNS7HZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/URHHSIBTPTALXMECRLAC2EVDNAFSR5NO
- https://security.gentoo.org/glsa/202208-06
- https://security.netapp.com/advisory/ntap-20220915-0006
