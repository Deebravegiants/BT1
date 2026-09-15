# [M] Code Injection, Race Condition, and Execution with Unnecessary Privileges in Ansible

## Summary
Severity: Medium
Advisory: GHSA-p62g-jhg6-v3rq
CVE: CVE-2020-10684
CWE: CWE-250, CWE-362, CWE-862, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-04-07
Source: https://github.com/advisories/GHSA-p62g-jhg6-v3rq
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.7.0a1 <2.7.17
- PyPI: `ansible` — affected >=2.8.0a1 <2.8.11
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.7

## Details
A flaw was found in Ansible Engine, all versions 2.7.x, 2.8.x and 2.9.x prior to 2.7.17, 2.8.11, and 2.9.7 respectively, when using ansible_facts as a subkey of itself and promoting it to a variable when inject is enabled, overwriting the ansible_facts after the clean. An attacker could take advantage of this by altering the ansible_facts, such as ansible_hosts, users and any other key data which would lead into privilege escalation or code injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10684
- https://github.com/ansible/ansible/commit/0b4788a71fc7d24ffa957a94ee5e23d6a9733ab0
- https://github.com/ansible/ansible/commit/1d0d2645eed36ac4e17052ab4eacf240132d96fb
- https://github.com/ansible/ansible/commit/5eabf7bb93c9bfc375b806a2b1f623d650cddc2b
- https://github.com/ansible/ansible/commit/a9d2ceafe429171c0e2ad007058b88bae57c74ce
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10684
- https://github.com/advisories/GHSA-p62g-jhg6-v3rq
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-207.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DKPA4KC3OJSUFASUYMG66HKJE7ADNGFW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MRRYUU5ZBLPBXCYG6CFP35D64NP2UB2S
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WQVOQD4VAIXXTVQAJKTN7NUGTJFE2PCB
- https://security.gentoo.org/glsa/202006-11
- https://www.debian.org/security/2021/dsa-4950
