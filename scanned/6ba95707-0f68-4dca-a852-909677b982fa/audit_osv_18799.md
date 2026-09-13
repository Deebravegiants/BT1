# [H] CVE-2020-36243

## Summary
Severity: High
Advisory: CVE-2020-36243
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-07
Source: https://osv.dev/vulnerability/CVE-2020-36243
Type: osv

## Details
The Patient Portal of OpenEMR 5.0.2.1 is affected by a Command Injection vulnerability in /interface/main/backup.php. To exploit the vulnerability, an authenticated attacker can send a POST request that executes arbitrary OS commands via shell metacharacters.

## References
- https://community.open-emr.org/t/openemr-5-0-2-patch-5-has-been-released/15431
- https://community.sonarsource.com/t/openemr-5-0-2-1-command-injection-vulnerability-puts-health-records-at-risk/33592
- https://www.open-emr.org/wiki/index.php/OpenEMR_Patches
- https://blog.sonarsource.com/openemr-5-0-2-1-command-injection-vulnerability
