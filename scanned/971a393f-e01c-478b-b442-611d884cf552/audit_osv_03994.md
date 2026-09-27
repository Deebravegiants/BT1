# [M] BIT-activemq-2020-13920

## Summary
Severity: Medium
Advisory: BIT-activemq-2020-13920
Aliases: CVE-2020-13920, GHSA-xgrx-xpv2-6vp4
Ecosystem: Bitnami
Published: 2025-12-03
Source: https://osv.dev/vulnerability/BIT-activemq-2020-13920
Type: osv

## Affected
- Bitnami: `activemq` — affected >=0 <5.15.12

## Details
Apache ActiveMQ uses LocateRegistry.createRegistry() to create the JMX RMI registry and binds the server to the "jmxrmi" entry. It is possible to connect to the registry without authentication and call the rebind method to rebind jmxrmi to something else. If an attacker creates another server to proxy the original, and bound that, he effectively becomes a man in the middle and is able to intercept the credentials when an user connects. Upgrade to Apache ActiveMQ 5.15.12.

## References
- http://activemq.apache.org/security-advisories.data/CVE-2020-13920-announcement.txt
- https://lists.apache.org/thread.html/r946488fb942fd35c6a6e0359f52504a558ed438574a8f14d36d7dcd7%40%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb2fd3bf2dce042e0ab3f3c94c4767c96bb2e7e6737624d63162df36d%40%3Ccommits.activemq.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/10/msg00013.html
- https://lists.debian.org/debian-lts-announce/2023/11/msg00013.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-13920
- https://www.oracle.com/security-alerts/cpuoct2020.html
