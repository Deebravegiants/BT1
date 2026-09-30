# [M] Okio Signed to Unsigned Conversion Error vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w33c-445m-f8w7
CVE: CVE-2023-3635
CWE: CWE-195, CWE-681
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-w33c-445m-f8w7
Type: github-advisory

## Affected
- Maven: `com.squareup.okio:okio` — affected >=2.0.0-RC1 <3.4.0
- Maven: `com.squareup.okio:okio` — affected >=0 <1.17.6
- Maven: `com.squareup.okio:okio-jvm` — affected >=2.0.0-RC1 <3.4.0

## Details
GzipSource does not handle an exception that might be raised when parsing a malformed gzip buffer. This may lead to denial of service of the Okio client when handling a crafted GZIP archive, by using the GzipSource class.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3635
- https://github.com/square/okio/pull/1280
- https://github.com/square/okio/pull/1334
- https://github.com/square/okio/commit/81bce1a30af244550b0324597720e4799281da7b
- https://github.com/square/okio/commit/b4fa875dc24950680c386e4b1c593660ce4f7839
- https://github.com/square/okio
- https://github.com/square/okio/blob/master/CHANGELOG.md#version-1176
- https://research.jfrog.com/vulnerabilities/okio-gzip-source-unhandled-exception-dos-xray-523195
