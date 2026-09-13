# [C] CVE-2018-11792

## Summary
Severity: Critical
Advisory: CVE-2018-11792
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-24
Source: https://osv.dev/vulnerability/CVE-2018-11792
Type: osv

## Details
In Apache Impala before 3.0.1, ALTER TABLE/VIEW RENAME required ALTER on the old table. This may pose a potential security risk, such as having ALTER on a table and ALL on a particular database allows a user to move the table to a database with ALL, which will automatically grant that user with ALL privilege on that table due to the privilege inherited from the database.

## References
- https://lists.apache.org/thread.html/cba8f18df15af862aa07c584d8dc85c44a199fb8f460edd498059247%40%3Cdev.impala.apache.org%3E
- http://www.securityfocus.com/bid/105739
