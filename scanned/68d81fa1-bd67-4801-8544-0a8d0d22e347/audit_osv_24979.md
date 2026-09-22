# [H] CVE-2023-29050

## Summary
Severity: High
Advisory: CVE-2023-29050
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:L)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-29050
Type: osv

## Details
The optional "LDAP contacts provider" could be abused by privileged users to inject LDAP filter strings that allow to access content outside of the intended hierarchy. Unauthorized users could break confidentiality of information in the directory and potentially cause high load on the directory server, leading to denial of service. Encoding has been added for user-provided fragments that are used when constructing the LDAP query. No publicly available exploits are known.

## References
- http://packetstormsecurity.com/files/176421/OX-App-Suite-7.10.6-XSS-Command-Execution-LDAP-Injection.html
- http://seclists.org/fulldisclosure/2024/Jan/3
- https://documentation.open-xchange.com/appsuite/security/advisories/csaf/2023/oxas-adv-2023-0005.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29050.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29050
- https://software.open-xchange.com/products/appsuite/doc/Release_Notes_for_Patch_Release_6248_7.10.6_2023-09-19.pdf
