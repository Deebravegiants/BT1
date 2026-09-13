# [C] CVE-2020-6144

## Summary
Severity: Critical
Advisory: CVE-2020-6144
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-01
Source: https://osv.dev/vulnerability/CVE-2020-6144
Type: osv

## Details
A remote code execution vulnerability exists in the install functionality of OS4Ed openSIS 7.4. The username variable which is set at line 121 in install/Step5.php allows for injection of PHP code into the Data.php file that it writes. An attacker can send an HTTP request to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1083
