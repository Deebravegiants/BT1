# [H] CVE-2018-15154

## Summary
Severity: High
Advisory: CVE-2018-15154
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-15
Source: https://osv.dev/vulnerability/CVE-2018-15154
Type: osv

## Details
OS command injection occurring in versions of OpenEMR before 5.0.1.4 allows a remote authenticated attacker to execute arbitrary commands by making a crafted request to interface/billing/sl_eob_search.php after modifying the "print_command" global variable in interface/super/edit_globals.php.

## References
- https://insecurity.sh/reports/openemr.pdf
- https://www.databreaches.net/openemr-patches-serious-vulnerabilities-uncovered-by-project-insecurity/
- https://github.com/openemr/openemr/pull/1757
- https://www.open-emr.org/wiki/index.php/OpenEMR_Patches
