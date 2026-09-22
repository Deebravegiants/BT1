# [H] CVE-2021-32101

## Summary
Severity: High
Advisory: CVE-2021-32101
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2021-05-07
Source: https://osv.dev/vulnerability/CVE-2021-32101
Type: osv

## Details
The Patient Portal of OpenEMR 5.0.2.1 is affected by a incorrect access control system in portal/patient/_machine_config.php. To exploit the vulnerability, an unauthenticated attacker can register an account, bypassing the permission check of this portal's API. Then, the attacker can then manipulate and read data of every registered patient.

## References
- https://blog.sonarsource.com/openemr-5-0-2-1-command-injection-vulnerability
- https://community.open-emr.org/t/openemr-5-0-2-patch-5-has-been-released/15431
- https://community.sonarsource.com/t/openemr-5-0-2-1-command-injection-vulnerability-puts-health-records-at-risk/33592
- https://portswigger.net/daily-swig/healthcare-security-openemr-fixes-serious-flaws-that-lead-to-command-execution-in-patient-portal
