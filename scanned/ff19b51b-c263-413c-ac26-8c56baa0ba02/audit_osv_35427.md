# [M] Python3.11-django-ansible-base: sensitive authenticator secrets returned in clear text via api in aap

## Summary
Severity: Medium
Advisory: CVE-2025-7738
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-31
Source: https://osv.dev/vulnerability/CVE-2025-7738
Type: osv

## Details
A flaw was found in Ansible Automation Platform (AAP) where the Gateway API returns the client secret for certain GitHub Enterprise authenticators in clear text. This vulnerability affects administrators or auditors accessing authenticator configurations. While access is limited to privileged users, the clear text exposure of sensitive credentials increases the risk of accidental leaks or misuse.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:12772
- https://access.redhat.com/security/cve/CVE-2025-7738
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7738.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-7738
- https://bugzilla.redhat.com/show_bug.cgi?id=2381589
- https://github.com/ansible/django-ansible-base/commit/e241ea4dce8df577eda15301e0a8e61be647b27b
- https://github.com/ansible/django-ansible-base/pull/773
- https://github.com/ansible/django-ansible-base
