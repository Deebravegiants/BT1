# [H] Improper Input Validation and Command Injection in Ansible

## Summary
Severity: High
Advisory: GHSA-2pfh-q76x-gwvm
CVE: CVE-2021-3583
CWE: CWE-20, CWE-77, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-09-23
Source: https://github.com/advisories/GHSA-2pfh-q76x-gwvm
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.9.23rc1
- PyPI: `ansible` — affected >=2.10.0a1 <2.10.11rc1
- PyPI: `ansible` — affected >=2.11.0a1 <2.11.2rc1

## Details
A flaw was found in Ansible, where a user's controller is vulnerable to template injection. This issue can occur through facts used in the template if the user is trying to put templates in multi-line YAML strings and the facts being handled do not routinely include special template characters. This flaw allows attackers to perform command injection, which discloses sensitive information. The highest threat from this vulnerability is to confidentiality and integrity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3583
- https://github.com/ansible/ansible/pull/74960
- https://github.com/ansible/ansible/commit/03aff644cc1c00e1f7551195c68fbd0d13a39e6e
- https://github.com/ansible/ansible/commit/8aa850e3573e48c9a2f12aef84e8a3a6f5ba4847
- https://github.com/ansible/ansible/commit/8b17e5b9229ffaecfe10a4881bc3f87dd2c184e1
- https://bugzilla.redhat.com/show_bug.cgi?id=1968412
- https://github.com/advisories/GHSA-2pfh-q76x-gwvm
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2021-358.yaml
- https://lists.debian.org/debian-lts-announce/2023/12/msg00018.html
