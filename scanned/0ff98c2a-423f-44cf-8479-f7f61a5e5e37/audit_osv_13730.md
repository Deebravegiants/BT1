# [H] CVE-2018-25021

## Summary
Severity: High
Advisory: CVE-2018-25021
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-12-13
Source: https://osv.dev/vulnerability/CVE-2018-25021
Type: osv

## Details
The TCP Server module in toxcore before 0.2.8 doesn't free the TCP priority queue under certain conditions, which allows a remote attacker to exhaust the system's memory, causing a denial of service (DoS).

## References
- https://blog.tox.chat/2018/10/memory-leak-bug-and-new-toxcore-release-fixing-it/
- https://github.com/TokTok/c-toxcore/pull/1216
- https://github.com/TokTok/c-toxcore/issues/1214
