# [M] Event-driven-ansible: exposure inventory passwords in plain text when starting a rulebook activation with verbosity set to debug in eda

## Summary
Severity: Medium
Advisory: CVE-2025-2877
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-28
Source: https://osv.dev/vulnerability/CVE-2025-2877
Type: osv

## Details
A flaw was found in the Ansible Automation Platform's Event-Driven Ansible. In configurations where verbosity is set to "debug", inventory passwords are exposed in plain text when starting a rulebook activation. This issue exists for any "debug" action in a rulebook and also affects Event Streams.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:3636
- https://access.redhat.com/errata/RHSA-2025:3637
- https://access.redhat.com/security/cve/CVE-2025-2877
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2877.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2877
- https://bugzilla.redhat.com/show_bug.cgi?id=2355540
- https://github.com/ansible/ansible-rulebook/pull/767
- https://github.com/ansible/ansible-rulebook
