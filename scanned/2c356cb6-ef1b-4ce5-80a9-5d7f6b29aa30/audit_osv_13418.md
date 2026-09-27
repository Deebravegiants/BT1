# [H] CVE-2018-19793

## Summary
Severity: High
Advisory: CVE-2018-19793
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-19793
Type: osv

## Details
jiacrontab 1.4.5 allows remote attackers to execute arbitrary commands via the crontab/task/edit?addr=localhost%3a20001 command and args parameters, as demonstrated by command=cat&args=/etc/passwd in the POST data.

## References
- https://github.com/iwannay/jiacrontab/issues/28
