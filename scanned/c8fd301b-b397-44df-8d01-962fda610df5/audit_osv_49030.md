# [C] CVE-2018-20752

## Summary
Severity: Critical
Advisory: CVE-2018-20752
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2018-20752
Type: osv

## Details
An issue was discovered in Recon-ng before 4.9.5. Lack of validation in the modules/reporting/csv.py file allows CSV injection. More specifically, when a Twitter user possesses an Excel macro for a username, it will not be properly sanitized when exported to a CSV file. This can result in remote code execution for the attacker.

## References
- https://bitbucket.org/LaNMaSteR53/recon-ng/issues/285/csv-injection-vulnerability-identified-in
- https://bitbucket.org/LaNMaSteR53/recon-ng/commits/41e96fd58891439974fb0c920b349f8926c71d4c#chg-modules/reporting/csv.py
