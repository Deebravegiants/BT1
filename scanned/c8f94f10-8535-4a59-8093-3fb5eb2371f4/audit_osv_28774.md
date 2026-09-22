# [H] CVE-2024-36467

## Summary
Severity: High
Advisory: CVE-2024-36467
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-27
Source: https://osv.dev/vulnerability/CVE-2024-36467
Type: osv

## Details
An authenticated user with API access (e.g.: user with default User role), more specifically a user with access to the user.update API endpoint is enough to be able to add themselves to any group (e.g.: Zabbix Administrators), except to groups that are disabled or having restricted GUI access.

## References
- https://support.zabbix.com/browse/ZBX-25614
