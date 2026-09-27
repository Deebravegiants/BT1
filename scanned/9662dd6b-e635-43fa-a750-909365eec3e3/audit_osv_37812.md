# [M] CVE-2026-33369

## Summary
Severity: Medium
Advisory: CVE-2026-33369
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33369
Type: osv

## Details
Zimbra Collaboration (ZCS) 10.0 and 10.1 contains an LDAP injection vulnerability in the Mailbox SOAP service within a FolderAction operation. The application fails to properly sanitize user-supplied input before incorporating it into an LDAP search filter. An authenticated attacker can exploit this issue by sending a crafted SOAP request that manipulates the LDAP query, allowing retrieval of sensitive directory attributes.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.1.16#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Responsible_Disclosure_Policy
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33369.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33369
