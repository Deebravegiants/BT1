# [C] Server-Side Template Injection in extension "powermail" (powermail)

## Summary
Severity: Critical
Advisory: CVE-2026-77136
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-77136
Type: osv

## Details
The extension passes the raw value of a form field configured as "This field contains the name of the sender" directly into a Fluid View as template source, without any sanitization, and renders it. An anonymous, unauthenticated user can submit Fluid template syntax in that field to execute arbitrary Fluid ViewHelpers leading to disclosure of server configuration, environment variables and application source, and potentially remote code execution. Exploitation requires only that a form field is configured as the sender_name field, a common and default-adjacent Powermail configuration. No authentication or user interaction beyond a normal form submission is required. This vulnerability is reported to be actively exploited in the wild.

## References
- https://packagist.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77136.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77136
- https://typo3.org/security/advisory/typo3-ext-sa-2026-022
- https://github.com/in2code-de/powermail
