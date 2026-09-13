# [C] Deserialization of Untrusted Data in Flamingo amf-serializer

## Summary
Severity: Critical
Advisory: GHSA-j88v-q3vw-p9vr
CVE: CVE-2017-3202
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j88v-q3vw-p9vr
Type: github-advisory

## Affected
- Maven: `com.exadel.flamingo.flex:amf-serializer` — affected >=0

## Details
The Java implementation of AMF3 deserializers used in Flamingo amf-serializer by Exadel, version 2.2.0, may allow instantiation of arbitrary classes via their public parameter-less constructor and subsequently call arbitrary Java Beans setter methods. The ability to exploit this vulnerability depends on the availability of classes in the class path that make use of deserialization. A remote attacker with the ability to spoof or control information may be able to send serialized Java objects with pre-set properties that result in arbitrary code execution when deserialized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3202
- https://codewhitesec.blogspot.com/2017/04/amf.html
- http://www.securityweek.com/flaws-java-amf-libraries-allow-remote-code-execution
