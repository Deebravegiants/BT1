# [C] CVE-2024-53438

## Summary
Severity: Critical
Advisory: CVE-2024-53438
Aliases: GHSA-gr5x-8j97-qq23
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-22
Source: https://osv.dev/vulnerability/CVE-2024-53438
Type: osv

## Details
EventAttendance.php in ChurchCRM 5.7.0 is vulnerable to SQL injection. An attacker can exploit this vulnerability by manipulating the 'Event' parameter, which is directly interpolated into the SQL query without proper sanitization or validation, allowing attackers to execute arbitrary SQL commands.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53438.json
- https://github.com/advisories/GHSA-gr5x-8j97-qq23
- https://nvd.nist.gov/vuln/detail/CVE-2024-53438
- https://github.com/ChurchCRM/CRM/issues/6988
