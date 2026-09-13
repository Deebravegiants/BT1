# [M] Inclusion of Sensitive Information in Log Files and Improper Output Neutralization for Logs in Ansible

## Summary
Severity: Medium
Advisory: GHSA-3m93-m4q6-mc6v
CVE: CVE-2019-14864
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-02-26
Source: https://github.com/advisories/GHSA-3m93-m4q6-mc6v
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.7.0a1 <2.7.15
- PyPI: `ansible` — affected >=2.8.0a1 <2.8.7
- PyPI: `ansible` — affected >=2.9.0a1 <2.9.1

## Details
Ansible, versions 2.9.x before 2.9.1, 2.8.x before 2.8.7 and Ansible versions 2.7.x before 2.7.15, is not respecting the flag no_log set it to True when Sumologic and Splunk callback plugins are used send tasks results events to collectors. This would discloses and collects any sensitive data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14864
- https://github.com/ansible/ansible/issues/63522
- https://github.com/ansible/ansible/pull/63527
- https://github.com/ansible/ansible/pull/64273
- https://github.com/ansible/ansible/pull/64274
- https://github.com/ansible/ansible/pull/64748
- https://github.com/ansible/ansible/commit/050f92f96054bf59e283fdec9972323c2ed00348
- https://github.com/ansible/ansible/commit/75288a89d0053d6df35c90863fb6c9542d89850e
- https://github.com/ansible/ansible/commit/a0ec2976b2716cdecdd7a8f416d96406acd79b7c
- https://github.com/ansible/ansible/commit/c76e074e4c71c7621a1ca8159261c1959b5287af
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14864
- https://github.com/advisories/GHSA-3m93-m4q6-mc6v
- https://github.com/ansible/ansible
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-160.yaml
- https://www.debian.org/security/2021/dsa-4950
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00026.html
