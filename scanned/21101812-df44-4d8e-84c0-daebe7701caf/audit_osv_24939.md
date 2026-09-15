# [H] GLPI vulnerable to account takeover by authenticated user

## Summary
Severity: High
Advisory: CVE-2023-28632
Aliases: GHSA-7pwm-pg76-3q9x
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-28632
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 0.83 and prior to versions 9.5.13 and 10.0.7, an authenticated user can modify emails of any user, and can therefore takeover another user account through the "forgotten password" feature. By modifying emails, the user can also receive sensitive data through GLPI notifications. Versions 9.5.13 and 10.0.7 contain a patch for this issue. As a workaround, account takeover can be prevented by deactivating all notifications related to `Forgotten password?` event. However, it will not prevent unauthorized modification of any user emails.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.7
- https://github.com/glpi-project/glpi/releases/tag/9.5.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28632.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-7pwm-pg76-3q9x
- https://nvd.nist.gov/vuln/detail/CVE-2023-28632
