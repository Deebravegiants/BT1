# [M] CVE-2019-15132

## Summary
Severity: Medium
Advisory: CVE-2019-15132
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-08-17
Source: https://osv.dev/vulnerability/CVE-2019-15132
Type: osv

## Details
Zabbix through 4.4.0alpha1 allows User Enumeration. With login requests, it is possible to enumerate application usernames based on the variability of server responses (e.g., the "Login name or password is incorrect" and "No permissions for system access" messages, or just blocking for a number of seconds). This affects both api_jsonrpc.php and index.php.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00013.html
- https://lists.debian.org/debian-lts-announce/2021/04/msg00018.html
- https://support.zabbix.com/browse/ZBX-16532
