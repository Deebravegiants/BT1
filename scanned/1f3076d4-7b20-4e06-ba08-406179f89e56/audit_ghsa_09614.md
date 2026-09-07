# [C] ajenti.plugin.core has password bypass when 2FA is activated

## Summary
Severity: Critical
Advisory: GHSA-3mcx-6wxm-qr8v
CVE: CVE-2026-40177
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-3mcx-6wxm-qr8v
Type: github-advisory

## Affected
- PyPI: `ajenti.plugin.core` — affected >=0 <0.112

## Details
### Impact

If the 2FA was activated, it was possible to bypass the password authentication

### Patches

This is fixed in the version 0.112. Users should upgrade to this version as soon as possible.

## References
- https://github.com/ajenti/ajenti/security/advisories/GHSA-3mcx-6wxm-qr8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-40177
- https://github.com/ajenti/ajenti
