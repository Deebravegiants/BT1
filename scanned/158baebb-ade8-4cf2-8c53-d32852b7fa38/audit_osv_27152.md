# [M] Automation-gateway: aap-gateway: improper scope handling in oauth2 tokens for aap 2.5

## Summary
Severity: Medium
Advisory: CVE-2024-11483
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2024-11-25
Source: https://osv.dev/vulnerability/CVE-2024-11483
Type: osv

## Details
A vulnerability was found in the Ansible Automation Platform (AAP). This flaw allows attackers to escalate privileges by improperly leveraging read-scoped OAuth2 tokens to gain write access. This issue affects API endpoints that rely on ansible_base.oauth2_provider for OAuth2 authentication. While the impact is limited to actions within the user’s assigned permissions, it undermines scoped access controls, potentially allowing unintended modifications in the application and consuming services.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:11145
- https://access.redhat.com/security/cve/CVE-2024-11483
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11483.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11483
- https://bugzilla.redhat.com/show_bug.cgi?id=2327579
- https://github.com/ansible/django-ansible-base/commit/845b3e1838cc0762a7f9f3e0379c5274519d9a44
- https://github.com/ansible/django-ansible-base
