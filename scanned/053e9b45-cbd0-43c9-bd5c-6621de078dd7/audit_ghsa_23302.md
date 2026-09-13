# [H] Ansible password prompts could expose passwords

## Summary
Severity: High
Advisory: GHSA-6fq2-x65v-v9h7
CVE: CVE-2019-14856
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6fq2-x65v-v9h7
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.8.0 <2.8.6
- PyPI: `ansible` — affected >=2.7.0 <2.7.14
- PyPI: `ansible` — affected >=2.6.0 <2.6.20

## Details
A data disclosure flaw was found in ansible. Password prompts in ansible-playbook and ansible-cli tools could expose passwords with special characters as they are not properly wrapped. A password with special characters is exposed starting with the first of these special characters. The highest threat from this vulnerability is to data confidentiality.

This CVE exists due to an incomplete fix for CVE-2019-10206.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14856
- https://github.com/ansible/ansible/pull/63351
- https://github.com/ansible/ansible/commit/16684f118715a52e1c46d437652add9ca36423de
- https://github.com/ansible/ansible/commit/2cbd8775ca1271195169f62122df1f88b532e74f
- https://github.com/ansible/ansible/commit/40618d70e61af1123907a5fb246cc4fd35f1e5c3
- https://github.com/ansible/ansible/commit/7f4befdea77045fa83b5f2b304bd5e16b219f74c
- https://access.redhat.com/errata/RHSA-2020:0756
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14856
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2019-146.yaml
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00026.html
