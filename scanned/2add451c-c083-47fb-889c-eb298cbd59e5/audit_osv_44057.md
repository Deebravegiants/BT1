# [C] RansomLook Missing Authorization in Web Configuration Editor Allows Application Configuration Modification

## Summary
Severity: Critical
Advisory: CVE-2026-78387
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78387
Type: osv

## Details
RansomLook contains an authorization weakness in the web-based configuration editor exposed through the /admin/config endpoint. The endpoint requires an authenticated session but does not perform an explicit privilege or administrator authorization check before allowing access to configuration-management functionality.

An authenticated low-privileged user able to access the endpoint can submit crafted configuration values that are written directly to the application's config/generic.json file. The affected functionality permits modification of configuration sections including notification, LDAP, SMTP, and general application settings. Successful exploitation could therefore allow an attacker to alter security-sensitive application behavior, redirect integrations or notifications, modify authentication-related configuration, disrupt external services, or render the RansomLook installation unavailable.

The configuration editor also operated on a configuration file containing sensitive values such as passwords, tokens, secrets, and API keys. Although the affected version contains logic intended to prevent recognized secret values from being returned to the browser, exposing configuration management through insufficiently authorized web functionality significantly increases the impact of a compromised or low-privileged account.

The patch resolves the issue by completely removing the /admin/config route and associated configuration-editing interface, preventing application configuration from being modified through the web UI.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78387.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78387
- https://github.com/RansomLook/RansomLook/commit/d411ff51446e9e8b04e15567b46d53e86a3116dd
- https://github.com/RansomLook/RansomLook
