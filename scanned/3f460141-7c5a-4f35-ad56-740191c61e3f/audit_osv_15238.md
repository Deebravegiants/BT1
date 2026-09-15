# [H] CVE-2019-14749

## Summary
Severity: High
Advisory: CVE-2019-14749
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-07
Source: https://osv.dev/vulnerability/CVE-2019-14749
Type: osv

## Details
An issue was discovered in osTicket before 1.10.7 and 1.12.x before 1.12.1. CSV (aka Formula) injection exists in the export spreadsheets functionality. These spreadsheets are generated dynamically from unvalidated or unfiltered user input in the Name and Internal Notes fields in the Users tab, and the Issue Summary field in the tickets tab. This allows other agents to download data in a .csv file format or .xls file format. This is used as input for spreadsheet applications such as Excel and OpenOffice Calc, resulting in a situation where cells in the spreadsheets can contain input from an untrusted source. As a result, the end user who is accessing the exported spreadsheet can be affected.

## References
- http://packetstormsecurity.com/files/154004/osTicket-1.12-Formula-Injection.html
- https://github.com/osTicket/osTicket/releases/tag/v1.10.7
- https://github.com/osTicket/osTicket/releases/tag/v1.12.1
- https://www.exploit-db.com/exploits/47225
- https://github.com/osTicket/osTicket/commit/99818486c5b1d8aa445cee232825418d6834f249
