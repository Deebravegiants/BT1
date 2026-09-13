# [H] Reusable Account Activation and Recovery Tokens Allow Repeated Account Takeover in vulnerability-lookup

## Summary
Severity: High
Advisory: CVE-2026-73431
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73431
Type: osv

## Details
Vulnerability-Lookup contains an 
authentication weakness in its account activation and password-recovery 
mechanism. Activation and recovery links were generated using stateless 
signed tokens containing only the user's login. Although the token 
signature and age were validated, the application did not track whether a
 token had already been successfully used. As a result, a captured 
activation or password-recovery link remained valid for the entire 
configured TOKEN_VALIDITY_PERIOD, even after the associated password had been changed. 


An attacker who obtains a valid 
activation or recovery token could therefore replay it multiple times 
during its validity period to set a new password and repeatedly take 
control of the affected account. In addition, tokens were not bound to a
 specific purpose, allowing the same token mechanism to be used across 
activation and recovery workflows. The patch introduces purpose-bound 
tokens and a random nonce whose SHA-256 digest is stored with the user 
account. The nonce is invalidated after a successful password change, 
making tokens single-use, while issuing a new token invalidates any 
previously issued token.  The password-setting operation now explicitly consumes the token before committing the account change. 


Successful exploitation requires 
the attacker to obtain a currently valid activation or recovery link, 
but does not require knowledge of the victim's existing password or an 
authenticated session.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73431.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73431
- https://github.com/vulnerability-lookup/vulnerability-lookup/commit/bef837242657acf680832be56b94428df130ed67
- https://github.com/vulnerability-lookup/vulnerability-lookup
