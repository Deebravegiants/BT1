# [C] MISP LDAP and LinOTP Authentication Bypass via Empty or Invalid Credentials

## Summary
Severity: Critical
Advisory: CVE-2026-85216
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85216
Type: osv

## Details
MISP contains an authentication bypass vulnerability in its LDAP and LinOTP authentication components due to insufficient validation of user-supplied credentials.

The custom LdapAuthenticate and LinOTPAuthenticate components replace CakePHP's FormAuthenticate implementation but did not replicate its credential validation checks. As a result, empty or non-string values could reach the underlying authentication mechanisms.

In the LDAP authentication path, an attacker able to identify a valid directory user's email address could submit an empty password. The empty credential could be passed to ldap_bind(), where an LDAP server accepting unauthenticated binds may return a successful result for a valid distinguished name combined with an empty password. MISP could consequently treat the attacker as the corresponding authenticated directory user without verification of the user's password.

The issue also affected the LinOTP authentication component. Invalid credential types were not rejected before being processed, and when mixed authentication was enabled, an empty password could be checked against a locally stored MISP password hash. LDAP-provisioned MISP accounts could additionally be created with an empty local password because account creation skipped normal validation, resulting in a hash corresponding to an empty password. This could permit authentication through the local fallback mechanism when such an account was no longer resolved through LDAP.

Successful exploitation could allow a remote unauthenticated attacker to impersonate an existing MISP user. If the targeted account has administrative or other privileged permissions, the attacker could gain corresponding access to sensitive threat-intelligence data, modify or delete information, alter configuration, or perform other privileged operations.

The patch resolves the vulnerability by requiring authentication identifiers and passwords to be valid strings, rejecting empty passwords where they are not explicitly permitted, and assigning a randomly generated local password to LDAP-provisioned accounts instead of storing a hash derived from an empty password.

## References
- https://github.com/MISP/MISP/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85216.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85216
- https://github.com/MISP/MISP/commit/0ee058548
