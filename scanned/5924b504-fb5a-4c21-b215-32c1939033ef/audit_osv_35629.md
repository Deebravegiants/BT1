# [C] Freeipa: idm: ipa: freeipa: obtaining tgs with impersonating cname through trust relationships

## Summary
Severity: Critical
Advisory: CVE-2026-11861
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-11861
Type: osv

## Details
A flaw was found in FreeIPA. When a trust relationship is configured between FreeIPA and Active Directory, Active Directory users can bypass authentication for FreeIPA services, including the portal, SMB server, and LDAP directory. This is possible by impersonating a client name in the Ticket Granting Service (TGS) due to FreeIPA services not verifying Privilege Attribute Certificate (PAC) certificates. This vulnerability could allow an authenticated Active Directory user to escalate their privileges within the FreeIPA domain.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-11861
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11861.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11861
- https://bugzilla.redhat.com/show_bug.cgi?id=2487472
