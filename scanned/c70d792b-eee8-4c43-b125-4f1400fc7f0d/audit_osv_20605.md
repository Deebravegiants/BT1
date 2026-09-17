# [C] CVE-2021-35502

## Summary
Severity: Critical
Advisory: CVE-2021-35502
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-25
Source: https://osv.dev/vulnerability/CVE-2021-35502
Type: osv

## Details
app/View/Elements/genericElements/IndexTable/Fields/generic_field.ctp in MISP 2.4.144 does not sanitize certain data related to generic-template:index.

## References
- https://github.com/MISP/MISP/commit/2fde6476dc3173affc61874ba2adb35400a8fda5
