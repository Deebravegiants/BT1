# [H] CVE-2018-12022

## Summary
Severity: High
Advisory: CVE-2018-12022
Aliases: GHSA-cjjf-94ff-43w7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2018-12022
Type: osv

## Details
An issue was discovered in FasterXML jackson-databind prior to 2.7.9.4, 2.8.11.2, and 2.9.6. When Default Typing is enabled (either globally or for a specific property), the service has the Jodd-db jar (for database access for the Jodd framework) in the classpath, and an attacker can provide an LDAP service to access, it is possible to make the service execute a malicious payload.

## References
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f%40%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/7fcf88aff0d1deaa5c3c7be8d58c05ad7ad5da94b59065d8e7c50c5d%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442%40%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc%40%3Cissues.drill.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZEDLDUYBSTDY4GWDBUXGJNS2RFYTFVRC/
- https://medium.com/%40cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- http://www.securityfocus.com/bid/107585
- https://access.redhat.com/errata/RHBA-2019:0959
- https://access.redhat.com/errata/RHSA-2019:0782
- https://access.redhat.com/errata/RHSA-2019:0877
- https://access.redhat.com/errata/RHSA-2019:1106
- https://access.redhat.com/errata/RHSA-2019:1107
- https://access.redhat.com/errata/RHSA-2019:1108
- https://access.redhat.com/errata/RHSA-2019:1140
- https://access.redhat.com/errata/RHSA-2019:1782
- https://access.redhat.com/errata/RHSA-2019:1797
- https://access.redhat.com/errata/RHSA-2019:1822
- https://access.redhat.com/errata/RHSA-2019:1823
- https://access.redhat.com/errata/RHSA-2019:2804
- https://access.redhat.com/errata/RHSA-2019:2858
