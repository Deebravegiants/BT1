# [H] ZoneMinder contains SQL Injection via report_event_audit

## Summary
Severity: High
Advisory: CVE-2023-26037
Aliases: GHSA-65jp-2hj3-3733
CVSS: 8.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2023-02-25
Source: https://osv.dev/vulnerability/CVE-2023-26037
Type: osv

## Details
ZoneMinder is a free, open source Closed-circuit television software application for Linux which supports IP, USB and Analog cameras. Versions prior to 1.36.33 and 1.37.33 contain an SQL Injection. The minTime and maxTime request parameters are not properly validated and could be used execute arbitrary SQL. This issue is fixed in versions 1.36.33 and 1.37.33.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26037.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-65jp-2hj3-3733
- https://nvd.nist.gov/vuln/detail/CVE-2023-26037
