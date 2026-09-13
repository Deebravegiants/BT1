# [H] logback serialization vulnerability

## Summary
Severity: High
Advisory: GHSA-vmq6-5m68-f53m
CVE: CVE-2023-6378
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-29
Source: https://github.com/advisories/GHSA-vmq6-5m68-f53m
Type: github-advisory

## Affected
- Maven: `ch.qos.logback:logback-classic` — affected >=1.3.0 <1.3.12
- Maven: `ch.qos.logback:logback-classic` — affected >=1.4.0 <1.4.12
- Maven: `ch.qos.logback:logback-core` — affected >=1.3.0 <1.3.12
- Maven: `ch.qos.logback:logback-core` — affected >=1.4.0 <1.4.12
- Maven: `ch.qos.logback:logback-core` — affected >=0 <1.2.13
- Maven: `ch.qos.logback:logback-classic` — affected >=0 <1.2.13

## Details
A serialization vulnerability in logback receiver component part of logback allows an attacker to mount a Denial-Of-Service attack by sending poisoned data.

This is only exploitable if logback receiver component is deployed. See https://logback.qos.ch/manual/receivers.html

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6378
- https://github.com/qos-ch/logback/issues/745#issuecomment-1836227158
- https://github.com/qos-ch/logback/commit/9c782b45be4abdafb7e17481e24e7354c2acd1eb
- https://github.com/qos-ch/logback/commit/b8eac23a9de9e05fb6d51160b3f46acd91af9731
- https://github.com/qos-ch/logback/commit/bb095154be011267b64e37a1d401546e7cc2b7c3
- https://github.com/qos-ch/logback
- https://logback.qos.ch/manual/receivers.html
- https://logback.qos.ch/news.html#1.2.13
- https://logback.qos.ch/news.html#1.3.12
- https://security.netapp.com/advisory/ntap-20241129-0012
