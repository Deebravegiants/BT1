# [H] Uncontrolled Resource Consumption in Artemis and HornetQ

## Summary
Severity: High
Advisory: GHSA-gc96-h5pr-839j
CVE: CVE-2017-12174
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gc96-h5pr-839j
Type: github-advisory

## Affected
- Maven: `org.hornetq:hornetq-server` — affected >=0 <2.4.0.Final
- Maven: `org.apache.activemq:artemis-native` — affected >=0 <2.4.0

## Details
It was found that when Artemis and HornetQ before 2.4.0 are configured with UDP discovery and JGroups discovery a huge byte array is created when receiving an unexpected multicast message. This may result in a heap memory exhaustion, full GC, or OutOfMemoryError.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12174
- https://access.redhat.com/errata/RHSA-2018:0268
- https://access.redhat.com/errata/RHSA-2018:0269
- https://access.redhat.com/errata/RHSA-2018:0270
- https://access.redhat.com/errata/RHSA-2018:0271
- https://access.redhat.com/errata/RHSA-2018:0275
- https://access.redhat.com/errata/RHSA-2018:0478
- https://access.redhat.com/errata/RHSA-2018:0479
- https://access.redhat.com/errata/RHSA-2018:0480
- https://access.redhat.com/errata/RHSA-2018:0481
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-12174
- https://lists.apache.org/thread.html/rb2fd3bf2dce042e0ab3f3c94c4767c96bb2e7e6737624d63162df36d%40%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb2fd3bf2dce042e0ab3f3c94c4767c96bb2e7e6737624d63162df36d@%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rc96ad63f148f784c84ea7f0a178c84a8985c6afccabbcd9847a82088%40%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rc96ad63f148f784c84ea7f0a178c84a8985c6afccabbcd9847a82088@%3Ccommits.activemq.apache.org%3E
