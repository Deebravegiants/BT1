# [H] Protobuf Java vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-4gg5-vx3j-xwc7
CVE: CVE-2022-3510
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-4gg5-vx3j-xwc7
Type: github-advisory

## Affected
- Maven: `com.google.protobuf:protobuf-java` — affected >=3.0.0 <3.16.3
- Maven: `com.google.protobuf:protobuf-java` — affected >=3.17.0 <3.19.6
- Maven: `com.google.protobuf:protobuf-java` — affected >=3.20.0 <3.20.3
- Maven: `com.google.protobuf:protobuf-java` — affected >=3.21.0 <3.21.7
- Maven: `com.google.protobuf:protobuf-javalite` — affected >=3.0.0 <3.16.3
- Maven: `com.google.protobuf:protobuf-javalite` — affected >=3.17.0 <3.19.6
- Maven: `com.google.protobuf:protobuf-javalite` — affected >=3.20.0 <3.20.3
- Maven: `com.google.protobuf:protobuf-javalite` — affected >=3.21.0 <3.21.7

## Details
A parsing issue similar to CVE-2022-3171, but with Message-Type Extensions in protobuf-java core and lite versions prior to 3.21.7, 3.20.3, 3.19.6 and 3.16.3 can lead to a denial of service attack. Inputs containing multiple instances of non-repeated embedded messages with repeated or unknown fields causes objects to be converted back-n-forth between mutable and immutable forms, resulting in potentially long garbage collection pauses. We recommend updating to the versions mentioned above.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3510
- https://github.com/protocolbuffers/protobuf/commit/db7c17803320525722f45c1d26fc08bc41d1bf48
- https://github.com/protocolbuffers/protobuf/tree/main/java
