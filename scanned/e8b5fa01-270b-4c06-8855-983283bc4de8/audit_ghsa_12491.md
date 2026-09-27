# [H] Logback is vulnerable to an attacker mounting a Denial-Of-Service attack by sending poisoned data

## Summary
Severity: High
Advisory: GHSA-gm62-rw4g-vrc4
CVE: CVE-2023-6481
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-04
Source: https://github.com/advisories/GHSA-gm62-rw4g-vrc4
Type: github-advisory

## Affected
- Maven: `ch.qos.logback:logback-core` — affected >=1.4.13 <1.4.14
- Maven: `ch.qos.logback:logback-core` — affected >=1.3.13 <1.3.14
- Maven: `ch.qos.logback:logback-core` — affected >=1.2.12 <1.2.13

## Details
A serialization vulnerability in logback receiver component part of logback version 1.4.13, 1.3.13 and 1.2.12 allows an attacker to mount a Denial-Of-Service attack by sending poisoned data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6481
- https://github.com/qos-ch/logback/commit/7018a3609c7bcc9dc7bf5903509901a986e5f578
- https://github.com/qos-ch/logback/commit/c612b2fa3caf6eef3c75f1cd5859438451d0fd6f
- https://github.com/qos-ch/logback
- https://logback.qos.ch/news.html#1.3.12
- https://logback.qos.ch/news.html#1.3.14
