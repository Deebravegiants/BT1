# [C] Improper Input Validation in PyYAML

## Summary
Severity: Critical
Advisory: GHSA-6757-jp84-gxfx
CVE: CVE-2020-1747
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-6757-jp84-gxfx
Type: github-advisory

## Affected
- PyPI: `pyyaml` — affected >=5.1b7 <5.3.1

## Details
A vulnerability was discovered in the PyYAML library in versions before 5.3.1, where it is susceptible to arbitrary code execution when it processes untrusted YAML files through the full_load method or with the FullLoader loader. Applications that use the library to process untrusted input may be vulnerable to this flaw. An attacker could use this flaw to execute arbitrary code on the system by abusing the python/object/new constructor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1747
- https://github.com/github/advisory-database/pull/4942
- https://github.com/yaml/pyyaml/pull/386
- https://github.com/yaml/pyyaml/commit/0cedb2a0697b2bc49e4f3841b8d4590b6b15657e
- https://github.com/yaml/pyyaml/commit/5080ba513377b6355a0502104846ee804656f1e0
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1747
- https://github.com/advisories/GHSA-6757-jp84-gxfx
- https://github.com/pypa/advisory-database/tree/main/vulns/pyyaml/PYSEC-2020-96.yaml
- https://github.com/yaml/pyyaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7PPAS6C4SZRDQLR7C22A5U3QOLXY33JX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/K5HEPD7LEVDPCITY5IMDYWXUMX37VFMY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MMQXSZXNJT6ERABJZAAICI3DQSQLCP3D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WORRFHPQVAFKKXXWLSSW6XKUYLWM6CSH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZBJA3SGNJKCAYPSHOHWY3KBCWNM5NYK2
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00017.html
