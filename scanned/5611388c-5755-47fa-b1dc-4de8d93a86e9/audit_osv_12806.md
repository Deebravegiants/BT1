# [M] CVE-2018-15141

## Summary
Severity: Medium
Advisory: CVE-2018-15141
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-08-13
Source: https://osv.dev/vulnerability/CVE-2018-15141
Type: osv

## Details
Directory traversal in portal/import_template.php in versions of OpenEMR before 5.0.1.4 allows a remote attacker authenticated in the patient portal to delete arbitrary files via the "docid" parameter when the mode is set to delete.

## References
- https://www.databreaches.net/openemr-patches-serious-vulnerabilities-uncovered-by-project-insecurity/
- https://github.com/openemr/openemr/pull/1765/files
- https://www.exploit-db.com/exploits/45202/
