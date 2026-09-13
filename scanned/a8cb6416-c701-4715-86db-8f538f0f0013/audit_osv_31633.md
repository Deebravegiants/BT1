# [H] Stored XSS in Psono-Client via Malicious Vault Entry URLs

## Summary
Severity: High
Advisory: CVE-2025-1987
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2025-06-21
Source: https://osv.dev/vulnerability/CVE-2025-1987
Type: osv

## Details
A Cross-Site Scripting (XSS) vulnerability has been identified in Psono-Client’s handling of vault entries of type website_password and bookmark, as used in Bitdefender SecurePass. The client does not properly sanitize the URL field in these entries. As a result, an attacker can craft a malicious vault entry (or trick a user into creating or importing one) with a javascript:URL. When the user interacts with this entry (for example, by clicking or opening it), the application will execute the malicious JavaScript in the context of the Psono vault. This allows an attacker to run arbitrary code in the victim’s browser, potentially giving them access to the user’s password vault and sensitive data.

## References
- https://bitdefender.com/support/support/security-advisories/stored-xss-in-psono-client-via-malicious-vault-entry-urls
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1987.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1987
