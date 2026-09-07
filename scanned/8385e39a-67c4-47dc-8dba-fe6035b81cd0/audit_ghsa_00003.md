# [H] Improper Privilege Management in Apache Karaf

## Summary
Severity: High
Advisory: GHSA-9448-c9wq-jg9v
CVE: CVE-2018-11786
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-9448-c9wq-jg9v
Type: github-advisory

## Affected
- Maven: `org.apache.karaf:apache-karaf` — affected >=0 <4.2.0

## Details
In Apache Karaf prior to 4.2.0 release, if the sshd service in Karaf is left on so an administrator can manage the running instance, any user with rights to the Karaf console can pivot and read/write any file on the file system to which the Karaf process user has access. This can be locked down a bit by using chroot to change the root directory to protect files outside of the Karaf install directory; it can be further locked down by defining a security manager policy that limits file system access to those directories beneath the Karaf home that are necessary for the system to run. However, this still allows anyone with ssh access to the Karaf process to read and write a large number of files as the Karaf process user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11786
- https://github.com/advisories/GHSA-9448-c9wq-jg9v
- https://issues.apache.org/jira/browse/KARAF-5427
- https://lists.apache.org/thread.html/5b7ac762c6bbe77ac5d9389f093fc6dbf196c36d788e3d7629e6c1d9@%3Cdev.karaf.apache.org%3E
- http://karaf.apache.org/security/cve-2018-11786.txt
