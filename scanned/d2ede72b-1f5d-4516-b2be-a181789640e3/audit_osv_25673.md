# [H] Samba: ad dc password exposure to privileged users and rodcs

## Summary
Severity: High
Advisory: CVE-2023-4154
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-07
Source: https://osv.dev/vulnerability/CVE-2023-4154
Type: osv

## Details
A design flaw was found in Samba's DirSync control implementation, which exposes passwords and secrets in Active Directory to privileged users and Read-Only Domain Controllers (RODCs). This flaw allows RODCs and users possessing the GET_CHANGES right to access all attributes, including sensitive secrets and passwords. Even in a default setup, RODC DC accounts, which should only replicate some passwords, can gain access to all domain secrets, including the vital krbtgt, effectively eliminating the RODC / DC distinction. Furthermore, the vulnerability fails to account for error conditions (fail open), like out-of-memory situations, potentially granting access to secret attributes, even under low-privileged attacker influence.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://packages.fedoraproject.org/
- https://www.samba.org/samba/security/CVE-2023-4154.html
- https://access.redhat.com/security/cve/CVE-2023-4154
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4154.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4154
- https://security.netapp.com/advisory/ntap-20231124-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2241883
- https://bugzilla.samba.org/show_bug.cgi?id=15424
