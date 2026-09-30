# [H] Ca: token authentication bypass vulnerability

## Summary
Severity: High
Advisory: CVE-2023-4727
Aliases: GHSA-rvm7-rc5g-c98q
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-11
Source: https://osv.dev/vulnerability/CVE-2023-4727
Type: osv

## Details
A flaw was found in dogtag-pki and pki-core. The token authentication scheme can be bypassed with a LDAP injection. By passing the query string parameter sessionID=*, an attacker can authenticate with an existing session saved in the LDAP directory server, which may lead to escalation of privilege.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://www.keycloak.org/
- https://access.redhat.com/errata/RHSA-2024:4051
- https://access.redhat.com/errata/RHSA-2024:4070
- https://access.redhat.com/errata/RHSA-2024:4164
- https://access.redhat.com/errata/RHSA-2024:4165
- https://access.redhat.com/errata/RHSA-2024:4179
- https://access.redhat.com/errata/RHSA-2024:4222
- https://access.redhat.com/errata/RHSA-2024:4367
- https://access.redhat.com/errata/RHSA-2024:4403
- https://access.redhat.com/errata/RHSA-2024:4413
- https://access.redhat.com/security/cve/CVE-2023-4727
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4727.json
- https://github.com/advisories/GHSA-rvm7-rc5g-c98q
- https://nvd.nist.gov/vuln/detail/CVE-2023-4727
- https://bugzilla.redhat.com/show_bug.cgi?id=2232218
- https://github.com/dogtagpki/pki/commit/54e5b3c5932ad634b5ddf5b1d4d88c9419d6f720
- https://github.com/dogtagpki/pki/commit/aa7161ba378caf5cf0471aafb679a842679c8388
