# [M] Ansible discloses sensitive information in traceback error message

## Summary
Severity: Medium
Advisory: GHSA-4r65-35qq-ch8j
CVE: CVE-2021-3620
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-4r65-35qq-ch8j
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <2.9.27

## Details
Ansible is an IT automation system that handles configuration management, application deployment, cloud provisioning, ad-hoc task execution, network automation, and multi-node orchestration. A flaw was found in Ansible Engine's ansible-connection module where sensitive information, such as the Ansible user credentials, is disclosed by default in the traceback error message when Ansible receives an unexpected response from `set_options`. The highest threat from this vulnerability is confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3620
- https://github.com/ansible/ansible/commit/fe28767970c8ec62aabe493c46b53a5de1e5fac0
- https://access.redhat.com/errata/RHSA-2021:3871
- https://access.redhat.com/errata/RHSA-2021:3872
- https://access.redhat.com/errata/RHSA-2021:3874
- https://access.redhat.com/errata/RHSA-2021:4703
- https://access.redhat.com/errata/RHSA-2021:4750
- https://access.redhat.com/security/cve/CVE-2021-3620
- https://bugzilla.redhat.com/show_bug.cgi?id=1975767
- https://github.com/advisories/GHSA-4r65-35qq-ch8j
- https://github.com/ansible/ansible
- https://github.com/ansible/ansible/blob/stable-2.9/changelogs/CHANGELOG-v2.9.rst#security-fixes
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2022-164.yaml
- https://lists.debian.org/debian-lts-announce/2023/12/msg00018.html
