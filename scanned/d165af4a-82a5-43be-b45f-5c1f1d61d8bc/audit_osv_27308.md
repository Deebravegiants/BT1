# [H] SQL Injection in parisneo/lollms-webui

## Summary
Severity: High
Advisory: CVE-2024-1601
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-1601
Type: osv

## Details
An SQL injection vulnerability exists in the `delete_discussion()` function of the parisneo/lollms-webui application, allowing an attacker to delete all discussions and message data. The vulnerability is exploitable via a crafted HTTP POST request to the `/delete_discussion` endpoint, which internally calls the vulnerable `delete_discussion()` function. By sending a specially crafted payload in the 'id' parameter, an attacker can manipulate SQL queries to delete all records from the 'discussion' and 'message' tables. This issue is due to improper neutralization of special elements used in an SQL command.

## References
- https://huntr.com/bounties/652a176e-6bd7-4161-8775-63a34ecc71d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1601.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1601
- https://github.com/parisneo/lollms-webui/commit/f0bc8f2babdfd4770a5adbf3b60ec612e4f1db46
