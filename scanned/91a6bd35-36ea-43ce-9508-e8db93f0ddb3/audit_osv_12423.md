# [M] CVE-2018-11785

## Summary
Severity: Medium
Advisory: CVE-2018-11785
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-10-24
Source: https://osv.dev/vulnerability/CVE-2018-11785
Type: osv

## Details
Missing authorization check in Apache Impala before 3.0.1 allows a Kerberos-authenticated but unauthorized user to inject random data into a running query, leading to wrong results for a query.

## References
- https://lists.apache.org/thread.html/cba8f18df15af862aa07c584d8dc85c44a199fb8f460edd498059247%40%3Cdev.impala.apache.org%3E
- http://www.securityfocus.com/bid/105742
