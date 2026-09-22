# [H] SQL injection in anuko timetracker

## Summary
Severity: High
Advisory: CVE-2022-24707
Aliases: GHSA-wqx7-95fx-wjxj
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2022-02-23
Source: https://osv.dev/vulnerability/CVE-2022-24707
Type: osv

## Details
Anuko Time Tracker is an open source, web-based time tracking application written in PHP. UNION SQL injection and time-based blind injection vulnerabilities existed in Time Tracker Puncher plugin in versions of anuko timetracker prior to 1.20.0.5642. This was happening because the Puncher plugin was reusing code from other places and was relying on an unsanitized date parameter in POST requests. Because the parameter was not checked, it was possible to craft POST requests with malicious SQL for Time Tracker database. This issue has been resolved in in version 1.20.0.5642. Users unable to upgrade are advised to add their own checks to input.

## References
- http://packetstormsecurity.com/files/167060/Anuko-Time-Tracker-1.20.0.5640-SQL-Injection.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24707.json
- https://github.com/anuko/timetracker/security/advisories/GHSA-wqx7-95fx-wjxj
- https://nvd.nist.gov/vuln/detail/CVE-2022-24707
- https://github.com/anuko/timetracker/commit/0e2d6563e2d969209c502a1eae4ddd8e87b73299
