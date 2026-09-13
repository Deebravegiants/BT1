# [M] Improper Output Neutralization and Improper Encoding or Escaping of Output for Logs in ansible

## Summary
Severity: Medium
Advisory: GHSA-785x-qw4v-6872
CVE: CVE-2020-14330
CWE: CWE-116, CWE-117, CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-785x-qw4v-6872
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.10.0

## Details
An Improper Output Neutralization for Logs flaw was found in Ansible when using the uri module, where sensitive data is exposed to content and json output. This flaw allows an attacker to access the logs or outputs of performed tasks to read keys used in playbooks from other users within the uri module. The highest threat from this vulnerability is to data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14330
- https://github.com/ansible/ansible/issues/68400
- https://github.com/ansible/ansible/pull/69653
- https://github.com/ansible/ansible/commit/e0f25a2b1f9e6c21f751ba0ed2dc2eee2152983e
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14330
- https://github.com/advisories/GHSA-785x-qw4v-6872
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-3.yaml
- https://www.debian.org/security/2021/dsa-4950
