# [C] GoCD vulnerable to admin privilege escalation by a malicious internal/existing authenticated user

## Summary
Severity: Critical
Advisory: CVE-2024-56320
Aliases: GHSA-346h-q594-rj8j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-01-03
Source: https://osv.dev/vulnerability/CVE-2024-56320
Type: osv

## Details
GoCD is a continuous deliver server. GoCD versions prior to 24.5.0 are vulnerable to admin privilege escalation due to improper authorization of access to the admin "Configuration XML" UI feature, and its associated API. A malicious insider/existing authenticated GoCD user with an existing GoCD user account could abuse this vulnerability to access information intended only for GoCD admins, or to escalate their privileges to that of a GoCD admin in a persistent manner. it is not possible for this vulnerability to be abused prior to authentication/login. The issue is fixed in GoCD 24.5.0. GoCD users who are not able to immediate upgrade can mitigate this issue by using a reverse proxy, WAF or similar to externally block access paths with a `/go/rails/` prefix. Blocking this route causes no loss of functionality. If it is not possible to upgrade or block the above route, consider reducing the GoCD user base to more trusted set of users, including temporarily disabling use of plugins such as the guest-login-plugin, which allow limited anonymous access as a regular user account.

## References
- https://github.com/gocd/gocd/releases/tag/24.5.0
- https://www.gocd.org/releases/#24-5-0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56320.json
- https://github.com/gocd/gocd/security/advisories/GHSA-346h-q594-rj8j
- https://nvd.nist.gov/vuln/detail/CVE-2024-56320
- https://github.com/gocd/gocd/commit/68b598b97bd283a5a85e20d018d69fe86acf4165
