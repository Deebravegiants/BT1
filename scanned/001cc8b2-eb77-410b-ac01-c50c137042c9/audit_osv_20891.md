# [C] CVE-2021-38145

## Summary
Severity: Critical
Advisory: CVE-2021-38145
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-31
Source: https://osv.dev/vulnerability/CVE-2021-38145
Type: osv

## Details
An issue was discovered in Form Tools through 3.0.20. SQL Injection can occur via the export_group_id field when a low-privileged user (client) tries to export a form with data, e.g., manipulation of modules/export_manager/export.php?export_group_id=1&export_group_1_results=all&export_type_id=1.

## References
- https://github.com/formtools/core/
- https://www.formtools.org/
- https://bernardofsr.github.io/blog/2021/form-tools/
- https://github.com/bernardofsr/CVEs-With-PoC/blob/main/PoCs/Form%20Tools/README.md
