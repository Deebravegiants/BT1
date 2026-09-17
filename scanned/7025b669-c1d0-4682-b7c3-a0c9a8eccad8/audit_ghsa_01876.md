# [H] Denial of Service (DoS) in Jackson Dataformat CBOR

## Summary
Severity: High
Advisory: GHSA-xmc8-26q4-qjhx
CVE: CVE-2020-28491
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-xmc8-26q4-qjhx
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.dataformat:jackson-dataformat-cbor` — affected >=2.8.0rc1 <2.11.4
- Maven: `com.fasterxml.jackson.dataformat:jackson-dataformat-cbor` — affected >=2.12.0rc1 <2.12.1

## Details
This affects the package com.fasterxml.jackson.dataformat:jackson-dataformat-cbor from 2.8.0-rc1 and before 2.11.4, from 2.12.0-rc1 and before 2.12.1. Unchecked allocation of byte buffer can cause a java.lang.OutOfMemoryError exception.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28491
- https://github.com/FasterXML/jackson-dataformats-binary/issues/186
- https://github.com/FasterXML/jackson-dataformats-binary/commit/3d7de83423f8f68f8e9a0c8250084e11818544c7
- https://github.com/FasterXML/jackson-dataformats-binary/commit/de072d314af8f5f269c8abec6930652af67bc8e6
- https://github.com/FasterXML/jackson-dataformats-binary
- https://snyk.io/vuln/SNYK-JAVA-COMFASTERXMLJACKSONDATAFORMAT-1047329
- https://www.oracle.com/security-alerts/cpujul2022.html
