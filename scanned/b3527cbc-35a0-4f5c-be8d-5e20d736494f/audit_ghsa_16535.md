# [M] Pterodactyl panel's admin area vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-384w-wffr-x63q
CVE: CVE-2024-34067
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-384w-wffr-x63q
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.11.6

## Details
### Impact

Importing a malicious egg or gaining access to wings instance could lead to XSS on the panel, which could be used to gain an administrator account on the panel. Specifically, the following things are impacted:
- Egg Docker images
- Egg variables:
    - Name
    - Environment variable
    - Default value
    - Description
    - Validation rules
 
Additionally, certain fields would reflect malicious input, but it would require the user knowingly entering such input to have an impact.

To iterate, this would require an administrator to perform actions and can't be triggered by a normal panel user.

### Workarounds

No workaround is available other than updating to the latest version of the panel.

### Patches

All of the following commits are required to resolve this security issue:

https://github.com/pterodactyl/panel/commit/1172d71d31561c4e465dabdf6b838e64de48ad16
https://github.com/pterodactyl/panel/commit/f671046947e4695b5e1c647df79305c1cefdf817
https://github.com/pterodactyl/panel/commit/0dad4c5a488661f9adc27dd311542516d9bfa0f2

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-384w-wffr-x63q
- https://nvd.nist.gov/vuln/detail/CVE-2024-34067
- https://github.com/pterodactyl/panel/commit/0dad4c5a488661f9adc27dd311542516d9bfa0f2
- https://github.com/pterodactyl/panel/commit/1172d71d31561c4e465dabdf6b838e64de48ad16
- https://github.com/pterodactyl/panel/commit/f671046947e4695b5e1c647df79305c1cefdf817
- https://github.com/pterodactyl/panel
