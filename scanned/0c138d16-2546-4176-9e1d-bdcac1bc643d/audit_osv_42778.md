# [H] ESPHome external_components file:// Scheme Validation Bypass Leading to Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2026-71259
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71259
Type: osv

## Details
ESPHome through 2026.7.0-dev contains an operator-precedence bug in the cv.url validator in esphome/config_validation.py. Because binds tighter than , any file: URI passes validation regardless of netloc. This validator gates the field of the external_components YAML directive's git source schema, which is passed to (git supports file:// natively).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71259.json
- https://github.com/esphome/esphome
- https://github.com/esphome/esphome/blob/dev/esphome/config_validation.py
- https://nvd.nist.gov/vuln/detail/CVE-2026-71259
