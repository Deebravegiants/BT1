# [H] CVE-2018-15142

## Summary
Severity: High
Advisory: CVE-2018-15142
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-13
Source: https://osv.dev/vulnerability/CVE-2018-15142
Type: osv

## Details
Directory traversal in portal/import_template.php in versions of OpenEMR before 5.0.1.4 allows a remote attacker authenticated in the patient portal to execute arbitrary PHP code by writing a file with a PHP extension via the "docid" and "content" parameters and accessing it in the traversed directory.

## References
- https://www.databreaches.net/openemr-patches-serious-vulnerabilities-uncovered-by-project-insecurity/
- https://github.com/openemr/openemr/pull/1765/files
- https://www.exploit-db.com/exploits/45202/
