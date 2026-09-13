# [H] CVE-2020-15255

## Summary
Severity: High
Advisory: CVE-2020-15255
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-10-16
Source: https://osv.dev/vulnerability/CVE-2020-15255
Type: osv

## Details
In Anuko Time Tracker before verion 1.19.23.5325, due to not properly filtered user input a CSV export of a report could contain cells that are treated as formulas by spreadsheet software (for example, when a cell value starts with an equal sign). This is fixed in version 1.19.23.5325.

## References
- https://github.com/anuko/timetracker/security/advisories/GHSA-prjf-9mgh-8fpv
- https://github.com/anuko/timetracker/commit/d9472904361495f318c9d0294ffd28acaaeae42f
- http://packetstormsecurity.com/files/159996/Anuko-Time-Tracker-1.19.23.5325-CSV-Injection.html
- https://www.exploit-db.com/exploits/49027
