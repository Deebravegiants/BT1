# [C] CVE-2021-40864

## Summary
Severity: Critical
Advisory: CVE-2021-40864
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-10
Source: https://osv.dev/vulnerability/CVE-2021-40864
Type: osv

## Details
The Translate plugin 6.1.x through 6.3.x before 6.3.0.72 for ONLYOFFICE Document Server lacks escape calls for the msg.data and text fields.

## References
- https://github.com/ONLYOFFICE/plugin-translator/commit/2206c0179cb97e3b8b290a0ab5719b1f0f54542b
- https://github.com/ONLYOFFICE/plugin-translator/compare/v6.3.0.71...v6.3.0.72
