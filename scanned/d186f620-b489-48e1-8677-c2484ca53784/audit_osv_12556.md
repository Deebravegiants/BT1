# [C] CVE-2018-1290

## Summary
Severity: Critical
Advisory: CVE-2018-1290
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-20
Source: https://osv.dev/vulnerability/CVE-2018-1290
Type: osv

## Details
In Apache Fineract versions 1.0.0, 0.6.0-incubating, 0.5.0-incubating, 0.4.0-incubating, Using a single quotation escape with two continuous SQL parameters can cause a SQL injection. This could be done in Methods like retrieveAuditEntries of AuditsApiResource Class and retrieveCommands of MakercheckersApiResource Class.

## References
- https://lists.apache.org/thread.html/69cc2b54b32f0936f40dc9be41f41fe1566710a75edbe2eb0a948ae4%40%3Cdev.fineract.apache.org%3E
- http://www.securityfocus.com/bid/103975
