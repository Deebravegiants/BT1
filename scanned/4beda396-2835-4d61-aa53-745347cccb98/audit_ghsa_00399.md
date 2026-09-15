# [C] Apache serialization mechanism does not have a list of classes allowed for serialization/deserialization

## Summary
Severity: Critical
Advisory: GHSA-chp4-rv79-68j3
CVE: CVE-2018-1295
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-chp4-rv79-68j3
Type: github-advisory

## Affected
- Maven: `org.apache.ignite:ignite-core` — affected >=0 <2.4

## Details
In Apache Ignite 2.3 or earlier, the serialization mechanism does not have a list of classes allowed for serialization/deserialization, which makes it possible to run arbitrary code when 3-rd party vulnerable classes are present in Ignite classpath. The vulnerability can be exploited if the one sends a specially prepared form of a serialized object to one of the deserialization endpoints of some Ignite components - discovery SPI, Ignite persistence, Memcached endpoint, socket steamer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1295
- https://access.redhat.com/errata/RHSA-2018:2405
- https://github.com/advisories/GHSA-chp4-rv79-68j3
- https://github.com/apache/ignite
- https://lists.apache.org/thread.html/45e7d5e2c6face85aab693f5ae0616563132ff757e5a558da80d0209@%3Cdev.ignite.apache.org%3E
- https://web.archive.org/web/20200227125559/http://www.securityfocus.com/bid/103692
