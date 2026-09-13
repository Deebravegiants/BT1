# [C] LDAP Tool Box Self Service Password 1.5.2 Account Takeover via HTTP Host Header

## Summary
Severity: Critical
Advisory: CVE-2023-53958
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2023-53958
Type: osv

## Details
LDAP Tool Box Self Service Password 1.5.2 contains a password reset vulnerability that allows attackers to manipulate HTTP Host headers during token generation. Attackers can craft malicious password reset requests that generate tokens sent to a controlled server, enabling potential account takeover by intercepting and using stolen reset tokens.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53958.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53958
- https://www.vulncheck.com/advisories/ldap-tool-box-self-service-password-account-takeover-via-http-host-header
- https://github.com/ltb-project/self-service-password
- https://www.exploit-db.com/exploits/51275
