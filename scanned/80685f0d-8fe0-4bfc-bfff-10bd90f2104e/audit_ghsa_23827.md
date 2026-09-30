# [M] Incorrect Authorization in Undertow

## Summary
Severity: Medium
Advisory: GHSA-cp7v-vmv7-6x2q
CVE: CVE-2017-12196
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cp7v-vmv7-6x2q
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=2.0.0.Alpha1 <2.0.2.FInal
- Maven: `io.undertow:undertow-core` — affected >=0 <1.4.24.Final

## Details
Undertow before versions 1.4.18.SP1 (not findable in Maven), 2.0.2.Final, and 1.4.24.Final was found vulnerable when using Digest authentication, the server does not ensure that the value of URI in the Authorization header matches the URI in HTTP request line. This allows the attacker to cause a MITM attack and access the desired content on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12196
- https://github.com/undertow-io/undertow/commit/facb33a5cedaf4b7b96d3840a08210370a806870
- https://access.redhat.com/errata/RHSA-2018:0478
- https://access.redhat.com/errata/RHSA-2018:0479
- https://access.redhat.com/errata/RHSA-2018:0480
- https://access.redhat.com/errata/RHSA-2018:0481
- https://access.redhat.com/errata/RHSA-2018:1525
- https://access.redhat.com/errata/RHSA-2018:2405
- https://access.redhat.com/errata/RHSA-2018:3768
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-12196
- https://github.com/undertow-io/undertow
- https://issues.jboss.org/browse/UNDERTOW-1190
