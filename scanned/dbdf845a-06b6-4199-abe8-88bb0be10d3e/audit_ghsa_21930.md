# [M] Injection in Apache Archiva

## Summary
Severity: Medium
Advisory: GHSA-v83p-xwm9-v4g8
CVE: CVE-2020-9495
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-v83p-xwm9-v4g8
Type: github-advisory

## Affected
- Maven: `org.apache.archiva:archiva` — affected >=0 <2.2.5

## Details
Apache Archiva login service before 2.2.5 is vulnerable to LDAP injection. A attacker is able to retrieve user attribute data from the connected LDAP server by providing special values to the login form. With certain characters it is possible to modify the LDAP filter used to query the LDAP users. By measuring the response time for the login request, arbitrary attribute data can be retrieved from LDAP user objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9495
- https://lists.apache.org/thread.html/r576eaabe3f772c045ec832a0200252494a2ce3f188f59450dd8f9b6d@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r576eaabe3f772c045ec832a0200252494a2ce3f188f59450dd8f9b6d@%3Cdev.archiva.apache.org%3E
- https://lists.apache.org/thread.html/r576eaabe3f772c045ec832a0200252494a2ce3f188f59450dd8f9b6d@%3Cusers.archiva.apache.org%3E
- https://lists.apache.org/thread.html/r7ae580f700ade57b00641a70a5c639a3ba576893bbf7f9fd93bc491d@%3Cusers.maven.apache.org%3E
- http://archiva.apache.org/security.html#CVE-2020-9495
- http://www.openwall.com/lists/oss-security/2020/06/19/1
