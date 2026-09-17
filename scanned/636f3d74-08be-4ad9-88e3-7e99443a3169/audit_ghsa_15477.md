# [H] protobuf-java has potential Denial of Service issue

## Summary
Severity: High
Advisory: GHSA-735f-pc8j-v9w8
CVE: CVE-2024-7254
CWE: CWE-20, CWE-400, CWE-787
Ecosystem: Maven, RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-19
Source: https://github.com/advisories/GHSA-735f-pc8j-v9w8
Type: github-advisory

## Affected
- Maven: `com.google.protobuf:protobuf-java` — affected >=0 <3.25.5
- Maven: `com.google.protobuf:protobuf-javalite` — affected >=0 <3.25.5
- Maven: `com.google.protobuf:protobuf-kotlin` — affected >=0 <3.25.5
- Maven: `com.google.protobuf:protobuf-kotlin-lite` — affected >=0 <3.25.5
- RubyGems: `google-protobuf` — affected >=0 <3.25.5
- RubyGems: `google-protobuf` — affected >=4.0.0.rc.1 <4.27.5
- RubyGems: `google-protobuf` — affected >=4.28.0.rc.1 <4.28.2
- Maven: `com.google.protobuf:protobuf-kotlin-lite` — affected >=4.0.0-RC1 <4.27.5
- Maven: `com.google.protobuf:protobuf-kotlin-lite` — affected >=4.28.0-RC1 <4.28.2
- Maven: `com.google.protobuf:protobuf-kotlin` — affected >=4.0.0-RC1 <4.27.5
- Maven: `com.google.protobuf:protobuf-kotlin` — affected >=4.28.0-RC1 <4.28.2
- Maven: `com.google.protobuf:protobuf-javalite` — affected >=4.0.0-RC1 <4.27.5
- Maven: `com.google.protobuf:protobuf-javalite` — affected >=4.28.0-RC1 <4.28.2
- Maven: `com.google.protobuf:protobuf-java` — affected >=4.0.0-RC1 <4.27.5
- Maven: `com.google.protobuf:protobuf-java` — affected >=4.28.0-RC1 <4.28.2

## Details
### Summary
When parsing unknown fields in the Protobuf Java Lite and Full library, a maliciously crafted message can cause a StackOverflow error and lead to a program crash.

Reporter: Alexis Challande, Trail of Bits Ecosystem Security Team <ecosystem@trailofbits.com>

Affected versions: This issue affects all versions of both the Java full and lite Protobuf runtimes, as well as Protobuf for Kotlin and JRuby, which themselves use the Java Protobuf runtime.

### Severity
[CVE-2024-7254](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-7254) **High** CVSS4.0 Score 8.7 (NOTE: there may be a delay in publication)
This is a potential Denial of Service. Parsing nested groups as unknown fields with DiscardUnknownFieldsParser or Java Protobuf Lite parser, or against Protobuf map fields, creates unbounded recursions that can be abused by an attacker.

### Proof of Concept
For reproduction details, please refer to the unit tests (Protobuf Java [LiteTest](https://github.com/protocolbuffers/protobuf/blob/a037f28ff81ee45ebe008c64ab632bf5372242ce/java/lite/src/test/java/com/google/protobuf/LiteTest.java) and [CodedInputStreamTest](https://github.com/protocolbuffers/protobuf/blob/a037f28ff81ee45ebe008c64ab632bf5372242ce/java/core/src/test/java/com/google/protobuf/CodedInputStreamTest.java)) that identify the specific inputs that exercise this parsing weakness.

### Remediation and Mitigation
We have been working diligently to address this issue and have released a mitigation that is available now. Please update to the latest available versions of the following packages:
* protobuf-java (3.25.5, 4.27.5, 4.28.2)
* protobuf-javalite (3.25.5, 4.27.5, 4.28.2)
* protobuf-kotlin (3.25.5, 4.27.5, 4.28.2)
* protobuf-kotlin-lite (3.25.5, 4.27.5, 4.28.2)
* com-protobuf [JRuby gem only] (3.25.5, 4.27.5, 4.28.2)

## References
- https://github.com/protocolbuffers/protobuf/security/advisories/GHSA-735f-pc8j-v9w8
- https://nvd.nist.gov/vuln/detail/CVE-2024-7254
- https://github.com/protocolbuffers/protobuf/commit/4728531c162f2f9e8c2ca1add713cfee2db6be3b
- https://github.com/protocolbuffers/protobuf/commit/850fcce9176e2c9070614dab53537760498c926b
- https://github.com/protocolbuffers/protobuf/commit/9a5f5fe752a20cbac2e722b06949ac985abdd534
- https://github.com/protocolbuffers/protobuf/commit/ac9fb5b4c71b0dd80985b27684e265d1f03abf46
- https://github.com/protocolbuffers/protobuf/commit/cc8b3483a5584b3301e3d43d17eb59704857ffaa
- https://github.com/protocolbuffers/protobuf/commit/d6c82fc55a76481c676f541a255571e8950bb8c3
- https://github.com/protocolbuffers/protobuf
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/google-protobuf/CVE-2024-7254.yml
- https://security.netapp.com/advisory/ntap-20241213-0010
- https://security.netapp.com/advisory/ntap-20250418-0006
