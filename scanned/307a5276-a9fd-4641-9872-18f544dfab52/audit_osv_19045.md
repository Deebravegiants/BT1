# [C] CVE-2020-6140

## Summary
Severity: Critical
Advisory: CVE-2020-6140
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-01
Source: https://osv.dev/vulnerability/CVE-2020-6140
Type: osv

## Details
SQL injection vulnerability exists in the password reset functionality of OS4Ed openSIS 7.3. The password_stf_email parameter in the password reset page /opensis/ResetUserInfo.php is vulnerable to SQL injection. An attacker can send an HTTP request to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1080
