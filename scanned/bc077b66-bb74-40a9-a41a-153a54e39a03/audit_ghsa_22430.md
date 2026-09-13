# [C] Missing certificate validation in Apache JMeter

## Summary
Severity: Critical
Advisory: GHSA-7v85-6hv2-rwgw
CVE: CVE-2018-1297
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7v85-6hv2-rwgw
Type: github-advisory

## Affected
- Maven: `org.apache.jmeter:ApacheJMeter` — affected >=0 <4.0

## Details
When using Distributed Test only (RMI based), Apache JMeter 2.x and 3.x uses an unsecured RMI connection. This could allow an attacker to get Access to JMeterEngine and send unauthorized code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1297
- https://github.com/apache/jmeter/issues/4677
- https://bz.apache.org/bugzilla/show_bug.cgi?id=62039
- https://github.com/apache/jmeter
- https://lists.apache.org/thread.html/31e0adbeca9d865ff74d0906b2248a41a1457cb54c1afbe5947df58b@%3Cissues.jmeter.apache.org%3E
- http://mail-archives.apache.org/mod_mbox/www-announce/201802.mbox/%3CCAH9fUpaNzk5am8oFe07RQ-kynCsQv54yB-uYs9bEnz7tbX-O7g%40mail.gmail.com%3E
