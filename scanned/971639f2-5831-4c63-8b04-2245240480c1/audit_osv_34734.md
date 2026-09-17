# [M] ServiceStack GetErrorResponse Improper Input Validation NTLM Relay Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-6444
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-6444
Type: osv

## Details
ServiceStack GetErrorResponse Improper Input Validation NTLM Relay Vulnerability. This vulnerability allows remote attackers to relay NTLM credentials on affected installations of ServiceStack. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the implementation of the GetErrorResponse method. The issue results from the lack of proper validation of user-supplied data, which can result in a type confusion condition. An attacker can leverage this vulnerability to relay NTLM credentials in the context of the current user. Was ZDI-CAN-25834.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6444.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6444
- https://www.zerodayinitiative.com/advisories/ZDI-25-415/
