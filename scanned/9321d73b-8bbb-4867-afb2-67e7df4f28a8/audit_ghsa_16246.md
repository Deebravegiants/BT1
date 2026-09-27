# [M] Ansible-core information disclosure flaw

## Summary
Severity: Medium
Advisory: GHSA-h24r-m9qc-pvpg
CVE: CVE-2024-0690
CWE: CWE-116, CWE-117
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-06
Source: https://github.com/advisories/GHSA-h24r-m9qc-pvpg
Type: github-advisory

## Affected
- PyPI: `ansible-core` — affected >=0 <2.14.14
- PyPI: `ansible-core` — affected >=2.16.0 <2.16.3
- PyPI: `ansible-core` — affected >=2.15.0 <2.15.9

## Details
An information disclosure flaw was found in ansible-core due to a failure to respect the `ANSIBLE_NO_LOG` configuration in some scenarios. It was discovered that information is still included in the output in certain tasks, such as loop items. Depending on the task, this issue may include sensitive information, such as decrypted secret values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0690
- https://github.com/ansible/ansible/pull/82565
- https://github.com/ansible/ansible/commit/6935c8e303440addd3871ecf8e04bde61080b032
- https://github.com/ansible/ansible/commit/78db3a3de6b40fb52d216685ae7cb903c609c3e1
- https://github.com/ansible/ansible/commit/b9a03bbf5a63459468baf8895ff74a62e9be4532
- https://github.com/ansible/ansible/commit/beb04bc2642c208447c5a936f94310528a1946b1
- https://access.redhat.com/errata/RHSA-2024:0733
- https://access.redhat.com/errata/RHSA-2024:2246
- https://access.redhat.com/errata/RHSA-2024:3043
- https://access.redhat.com/security/cve/CVE-2024-0690
- https://bugzilla.redhat.com/show_bug.cgi?id=2259013
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible-core/PYSEC-2024-36.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IZQGCRDSZL7ONCULMB6ZUHOE4L44KIBP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VDYSWOCPZMNRU5LWKIEBW4WGWLMTU7WQ
- https://security.netapp.com/advisory/ntap-20250117-0001
