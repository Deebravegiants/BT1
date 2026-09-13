# [M] Ansible-core: exposure of sensitive information in ansible vault files due to improper logging

## Summary
Severity: Medium
Advisory: CVE-2024-8775
Aliases: GHSA-jpxc-vmjf-9fcj, PYSEC-2026-1124
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-14
Source: https://osv.dev/vulnerability/CVE-2024-8775
Type: osv

## Details
A flaw was found in Ansible, where sensitive information stored in Ansible Vault files can be exposed in plaintext during the execution of a playbook. This occurs when using tasks such as include_vars to load vaulted variables without setting the no_log: true parameter, resulting in sensitive data being printed in the playbook output or logs. This can lead to the unintentional disclosure of secrets like passwords or API keys, compromising security and potentially allowing unauthorized access or actions.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://lists.debian.org/debian-lts-announce/2024/11/msg00021.html
- https://access.redhat.com/errata/RHSA-2024:10762
- https://access.redhat.com/errata/RHSA-2024:8969
- https://access.redhat.com/errata/RHSA-2024:9894
- https://access.redhat.com/errata/RHSA-2025:1249
- https://access.redhat.com/security/cve/CVE-2024-8775
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8775.json
- https://github.com/advisories/GHSA-jpxc-vmjf-9fcj
- https://nvd.nist.gov/vuln/detail/CVE-2024-8775
- https://bugzilla.redhat.com/show_bug.cgi?id=2312119
- https://github.com/ansible/ansible
