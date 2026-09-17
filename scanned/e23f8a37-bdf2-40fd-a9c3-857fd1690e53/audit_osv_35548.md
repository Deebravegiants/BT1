# [M] OTP bypass via plugin-based LDAP authentication in MISP when LDAP mixed authentication is enabled

## Summary
Severity: Medium
Advisory: CVE-2026-10611
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-10611
Type: osv

## Details
An authentication bypass vulnerability exists in MISP when LDAP mixed authentication is enabled with OTP enforcement. In deployments configured with LdapAuth.mixedAuth=true and Security.require_otp=true, users authenticated through an authentication plugin, such as LDAP, may have their authenticated session established during the application beforeFilter phase before the normal login flow enforces the OTP challenge.



As a result, an attacker with valid primary authentication credentials could bypass the required OTP step by authenticating through the plugin-backed login flow and then directly accessing another application URL instead of completing the OTP verification page. This allows access to the application as the affected user without providing a valid TOTP, HOTP, or email OTP code.



The issue affects configurations where plugin-based authentication is enabled and OTP is expected to be mandatory. The fix ensures that OTP requirements are checked immediately after plugin authentication and before the user session is established, redirecting users to the appropriate OTP challenge when required.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10611.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10611
- https://github.com/MISP/MISP/commit/39b3cb15aac4318afdd2ab63b96c2eac12b271fe
