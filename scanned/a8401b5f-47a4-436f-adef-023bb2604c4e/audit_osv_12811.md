# [H] CVE-2018-15146

## Summary
Severity: High
Advisory: CVE-2018-15146
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-15
Source: https://osv.dev/vulnerability/CVE-2018-15146
Type: osv

## Details
SQL injection vulnerability in interface/de_identification_forms/find_immunization_popup.php in versions of OpenEMR before 5.0.1.4 allows a remote authenticated attacker to execute arbitrary SQL commands via the 'search_term' parameter.

## References
- https://github.com/openemr/openemr/pull/1757/files
- https://www.databreaches.net/openemr-patches-serious-vulnerabilities-uncovered-by-project-insecurity/
- https://www.open-emr.org/wiki/index.php/OpenEMR_Patches
- https://insecurity.sh/reports/openemr.pdf
