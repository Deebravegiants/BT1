# [M] Insecure Flask Secret-Key File Permissions Allow Local Administrator Session Forgery in RansomLook

## Summary
Severity: Medium
Advisory: CVE-2026-78553
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78553
Type: osv

## Details
RansomLook created its Flask session-signing key without explicitly restricting the file permissions. The secret_key file was created using the process's default permissions and umask, resulting in permissions such as 0644 under a common 022 umask. Consequently, other local users able to access the RansomLook home directory could read the application's cryptographic secret.


The exposed key is security-critical because it is used to sign Flask session cookies and is also involved in the legacy API-key key derivation. An attacker who obtains the key can generate valid session cookies and impersonate an authenticated user, including an administrator. In LDAP configurations, exploitation may be particularly straightforward because the session user loader does not require the supplied username to correspond to an existing local user.


Successful exploitation requires local access sufficient to read the improperly protected file, but can result in complete compromise of RansomLook's authentication and authorization controls.


The patch creates new secret-key files atomically with permissions 0600 and also restricts permissions on existing key files during application startup.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78553.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78553
- https://github.com/RansomLook/RansomLook/commit/df9d47edcf02dd0125db869d5bc19d93f426d892
- https://github.com/RansomLook/RansomLook
