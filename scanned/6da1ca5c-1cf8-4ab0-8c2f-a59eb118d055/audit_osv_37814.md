# [M] CVE-2026-33371

## Summary
Severity: Medium
Advisory: CVE-2026-33371
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33371
Type: osv

## Details
An issue was discovered in Zimbra Collaboration (ZCS) 10.0 and 10.1. An XML External Entity (XXE) vulnerability exists in the Zimbra Exchange Web Services (EWS) SOAP interface due to improper handling of XML input. An authenticated attacker can submit crafted XML data that is processed by an XML parser with external entity resolution enabled. Successful exploitation may allow disclosure of sensitive local files from the server.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.1.16#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Responsible_Disclosure_Policy
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33371.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33371
