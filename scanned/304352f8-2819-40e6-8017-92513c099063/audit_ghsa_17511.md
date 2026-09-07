# [M] Laravel Translation Manager Vulnerable to Stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-j226-63j7-qrqh
CVE: CVE-2025-49130
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-j226-63j7-qrqh
Type: github-advisory

## Affected
- Packagist: `barryvdh/laravel-translation-manager` — affected >=0 <0.6.8

## Details
### Impact
The application is vulnerable to Cross-Site Scripting (XSS) attacks due to incorrect input validation and sanitization of user-input data. An attacker can inject arbitrary HTML code, including JavaScript scripts, into the page processed by the user's browser, allowing them to steal sensitive data, hijack user sessions, or conduct other malicious activities.

### Patches
The issue is fixed in https://github.com/barryvdh/laravel-translation-manager/pull/475 which is released in version 0.6.8

### Workarounds
Only authenticated users with access to the translation manager are impacted.

### References
[[PT-2025-04] laravel translation manager.pdf](https://github.com/user-attachments/files/20639250/PT-2025-04.laravel.translation.manager.pdf)

### Reported by
Positive Technologies (Artem Deikov, Ilya Tsaturov, Daniil Satyaev, Roman Cheremnykh, Artem Danilov, Stanislav Gleym)

## References
- https://github.com/barryvdh/laravel-translation-manager/security/advisories/GHSA-j226-63j7-qrqh
- https://nvd.nist.gov/vuln/detail/CVE-2025-49130
- https://github.com/barryvdh/laravel-translation-manager/pull/475
- https://github.com/barryvdh/laravel-translation-manager/commit/527446ed419f90f2319675fc5211cb8f851d7a1f
- https://github.com/barryvdh/laravel-translation-manager
- https://github.com/barryvdh/laravel-translation-manager/releases/tag/v0.6.8
