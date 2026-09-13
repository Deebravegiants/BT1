# [C] CVE-2018-1287

## Summary
Severity: Critical
Advisory: CVE-2018-1287
Aliases: GHSA-j7j7-g4ww-pxg5
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-14
Source: https://osv.dev/vulnerability/CVE-2018-1287
Type: osv

## Details
In Apache JMeter 2.X and 3.X, when using Distributed Test only (RMI based), jmeter server binds RMI Registry to wildcard host. This could allow an attacker to get Access to JMeterEngine and send unauthorized code.

## References
- https://lists.apache.org/thread.html/31e0adbeca9d865ff74d0906b2248a41a1457cb54c1afbe5947df58b%40%3Cissues.jmeter.apache.org%3E
- http://mail-archives.apache.org/mod_mbox/www-announce/201802.mbox/%3CCAH9fUpYsFx1%2Brwz1A%3Dmc7wAgbDHARyj1VrWNg41y9OySuL1mqw%40mail.gmail.com%3E
- http://www.securityfocus.com/bid/103068
