# [H] NiceGUI On Air authentication issue

## Summary
Severity: High
Advisory: GHSA-v6jv-p6r8-j78w
CVE: CVE-2025-21618
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-01-06
Source: https://github.com/advisories/GHSA-v6jv-p6r8-j78w
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <2.9.1

## Details
### Summary
Once a user logins to one browser, all other browsers are logged in without entering password. Even incognito mode.

### Impact
high

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-v6jv-p6r8-j78w
- https://nvd.nist.gov/vuln/detail/CVE-2025-21618
- https://github.com/zauberzeug/nicegui/commit/1621a4ba6a06676b8094362d36623551e651adc1
- https://github.com/zauberzeug/nicegui
