# [M] CVE-2020-13977

## Summary
Severity: Medium
Advisory: CVE-2020-13977
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-06-09
Source: https://osv.dev/vulnerability/CVE-2020-13977
Type: osv

## Details
Nagios 4.4.5 allows an attacker, who already has administrative access to change the "URL for JSON CGIs" configuration setting, to modify the Alert Histogram and Trends code via crafted versions of the archivejson.cgi, objectjson.cgi, and statusjson.cgi files. NOTE: this vulnerability has been mistakenly associated with CVE-2020-1408.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5P6NHNG2SJAM6DXVTXQH3AOJ4WQVKJUE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H7T6MSDWMBJEVVFSOK7DOYJJWDAFQCEQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JUEIABR4Y6L5J5MZDFWU46ZWXMJO64U3/
- https://github.com/sawolf/nagioscore/tree/url-injection-fix
- https://www.nagios.org/projects/nagios-core/history/4x/
- https://anhtai.me/nagios-core-4-4-5-url-injection/
