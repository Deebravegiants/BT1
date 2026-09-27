# [H] Ipa: privilege escalation via krbcanonicalname manipulation due to realm-unaware uniqueness enforcement in freeipa ldap datastore

## Summary
Severity: High
Advisory: CVE-2026-13097
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-13097
Type: osv

## Details
A privilege escalation flaw was found in FreeIPA. The uniqueness constraint enforced on Kerberos principal name attributes in the 389-ds directory server does not properly account for equivalent representations of the same principal name, allowing a user with sufficient LDAP write privileges to create a service principal that impersonates an existing privileged one. This can lead to unauthorized acquisition of Kerberos service tickets for sensitive services, potentially resulting in full domain compromise.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-13097
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13097.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13097
- https://bugzilla.redhat.com/show_bug.cgi?id=2515974
