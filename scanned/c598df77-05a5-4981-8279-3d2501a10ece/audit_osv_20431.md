# [H] CVE-2021-33580

## Summary
Severity: High
Advisory: CVE-2021-33580
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-18
Source: https://osv.dev/vulnerability/CVE-2021-33580
Type: osv

## Details
User controlled `request.getHeader("Referer")`, `request.getRequestURL()` and `request.getQueryString()` are used to build and run a regex expression. The attacker doesn't have to use a browser and may send a specially crafted Referer header programmatically. Since the attacker controls the string and the regex pattern he may cause a ReDoS by regex catastrophic backtracking on the server side. This problem has been fixed in Roller 6.0.2.

## References
- http://www.openwall.com/lists/oss-security/2021/08/18/1
- https://lists.apache.org/thread.html/r9d967d80af941717573e531db2c7353a90bfd0886e9b5d5d79f75506%40%3Cuser.roller.apache.org%3E
