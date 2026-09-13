# [H] Path Traversal in Ansible

## Summary
Severity: High
Advisory: GHSA-893h-35v4-mxqx
CVE: CVE-2020-1737
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-893h-35v4-mxqx
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.8.0a1 <2.8.9
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.6
- PyPI: `ansible` — affected >=0 <2.7.17

## Details
A flaw was found in Ansible 2.7.17 and prior, 2.8.9 and prior, and 2.9.6 and prior when using the Extract-Zip function from the win_unzip module as the extracted file(s) are not checked if they belong to the destination folder. An attacker could take advantage of this flaw by crafting an archive anywhere in the file system, using a path traversal. This issue is fixed in 2.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1737
- https://github.com/ansible/ansible/issues/67795
- https://github.com/ansible/ansible/pull/67799
- https://github.com/samdoran/ansible/commit/1de638b4d38d6d916588e2ad48d01f90dab8c36d
- https://github.com/samdoran/ansible/commit/aaf549d7870b8687209a3282841b59207735b676
- https://github.com/samdoran/ansible/commit/b60aa26e2313a8d52c0e0d3fd01696e797605b72
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1737
- https://github.com/advisories/GHSA-893h-35v4-mxqx
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-9.yaml
- https://github.com/samdoran/ansible
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FWDK3QUVBULS3Q3PQTGEKUQYPSNOU5M3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QT27K5ZRGDPCH7GT3DRI3LO4IVDVQUB7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U3IMV3XEIUXL6S4KPLYYM4TVJQ2VNEP2
- https://security.gentoo.org/glsa/202006-11
