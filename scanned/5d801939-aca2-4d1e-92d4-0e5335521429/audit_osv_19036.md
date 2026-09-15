# [H] CVE-2020-6131

## Summary
Severity: High
Advisory: CVE-2020-6131
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-01
Source: https://osv.dev/vulnerability/CVE-2020-6131
Type: osv

## Details
SQL injection vulnerabilities exist in the course_period_id parameters used in OS4Ed openSIS 7.3 pages. The course_period_id parameter in the page MassScheduleSessionSet.php is vulnerable to SQL injection. An attacker can make an authenticated HTTP request to trigger these vulnerabilities.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1076
