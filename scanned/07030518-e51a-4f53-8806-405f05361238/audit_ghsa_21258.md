# [H] Ansible leaks password to logs

## Summary
Severity: High
Advisory: GHSA-cpx3-93w7-457x
CVE: CVE-2022-3697
CWE: CWE-233
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-28
Source: https://github.com/advisories/GHSA-cpx3-93w7-457x
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.5.0 <7.0.0

## Details
A flaw was found in Ansible in the amazon.aws collection when using the `tower_callback` parameter from the `amazon.aws.ec2_instance` module. This flaw allows an attacker to take advantage of this issue as the module is handling the parameter insecurely, leading to the password leaking in the logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3697
- https://github.com/ansible-collections/amazon.aws/pull/1199
- https://github.com/ansible/ansible/pull/35749
- https://github.com/ansible-community/ansible-build-data/blob/main/6/CHANGELOG-v6.rst
- https://github.com/ansible/ansible
- https://lists.debian.org/debian-lts-announce/2023/12/msg00018.html
