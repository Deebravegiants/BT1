# [M] CVE-2018-20244

## Summary
Severity: Medium
Advisory: CVE-2018-20244
Aliases: GHSA-99cv-8cvv-666c, PYSEC-2019-142
CVSS: 5.5 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N)
Published: 2019-02-27
Source: https://osv.dev/vulnerability/CVE-2018-20244
Type: osv

## Details
In Apache Airflow before 1.10.2, a malicious admin user could edit the state of objects in the Airflow metadata database to execute arbitrary javascript on certain page views.

## References
- https://lists.apache.org/thread.html/2de387213d45bc626d27554a1bde7b8c67d08720901f82a50b6f4231%40%3Cdev.airflow.apache.org%3E
- https://lists.apache.org/thread.html/f656fddf9c49293b3ec450437c46709eb01a12d1645136b2f1b8573b%40%3Cdev.airflow.apache.org%3E
- http://www.openwall.com/lists/oss-security/2019/04/10/6
