# [M] Incorrect Permission Assignment for Critical Resource in Ansible

## Summary
Severity: Medium
Advisory: GHSA-x7jh-595q-wq82
CVE: CVE-2020-1736
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-x7jh-595q-wq82
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.7.0

## Details
A flaw was found in Ansible Engine when a file is moved using atomic_move primitive as the file mode cannot be specified. This sets the destination files world-readable if the destination file does not exist and if the file exists, the file could be changed to have less restrictive permissions before the move. This could lead to the disclosure of sensitive data. All versions in 2.7.x, 2.8.x and 2.9.x branches are believed to be vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1736
- https://github.com/ansible/ansible/issues/67794
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1736
- https://github.com/advisories/GHSA-x7jh-595q-wq82
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-8.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2NYYQP2XJB2TTRP6AKWVMBSPB2DFJNKD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BPNZWBAUP4ZHUR6PO7U6ZXEKNCX62KZ7
- https://security.gentoo.org/glsa/202006-11
