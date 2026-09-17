# [C] CVE-2021-3286

## Summary
Severity: Critical
Advisory: CVE-2021-3286
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2021-3286
Type: osv

## Details
SQL injection exists in Spotweb 1.4.9 because the notAllowedCommands protection mechanism is inadequate, e.g., a variation of the payload may be used. NOTE: this issue exists because of an incomplete fix for CVE-2020-35545.

## References
- https://github.com/spotweb/spotweb/issues/653
