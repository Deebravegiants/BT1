# [C] CVE-2019-14892

## Summary
Severity: Critical
Advisory: CVE-2019-14892
Aliases: GHSA-cf6r-3wgc-h863
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-02
Source: https://osv.dev/vulnerability/CVE-2019-14892
Type: osv

## Details
A flaw was discovered in jackson-databind in versions before 2.9.10, 2.8.11.5 and 2.6.7.3, where it would permit polymorphic deserialization of a malicious object using commons-configuration 1 and 2 JNDI classes. An attacker could use this flaw to execute arbitrary code.

## References
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf1bbc0ea4a9f014cf94df9a12a6477d24a27f52741dbc87f2fd52ff2%40%3Cissues.geode.apache.org%3E
- https://access.redhat.com/errata/RHSA-2020:0729
- https://security.netapp.com/advisory/ntap-20200904-0005/
- https://github.com/FasterXML/jackson-databind/issues/2462
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14892
