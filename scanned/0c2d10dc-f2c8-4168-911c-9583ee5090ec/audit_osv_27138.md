# [M] Ansible-core: unsafe tagging bypass via hostvars object in ansible-core

## Summary
Severity: Medium
Advisory: CVE-2024-11079
Aliases: GHSA-99w6-3xph-cx78, PYSEC-2026-1123
CVSS: 5.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:L)
Published: 2024-11-11
Source: https://osv.dev/vulnerability/CVE-2024-11079
Type: osv

## Details
A flaw was found in Ansible-Core. This vulnerability allows attackers to bypass unsafe content protections using the hostvars object to reference and execute templated content. This issue can lead to arbitrary code execution if remote data or module outputs are improperly templated within playbooks.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://lists.debian.org/debian-lts-announce/2026/03/msg00006.html
- https://access.redhat.com/errata/RHSA-2024:10770
- https://access.redhat.com/errata/RHSA-2024:11145
- https://access.redhat.com/security/cve/CVE-2024-11079
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11079.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11079
- https://bugzilla.redhat.com/show_bug.cgi?id=2325171
- https://github.com/ansible/ansible
