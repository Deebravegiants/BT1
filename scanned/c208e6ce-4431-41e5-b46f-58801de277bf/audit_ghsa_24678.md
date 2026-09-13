# [H] GraniteDS Insecure Deserialization

## Summary
Severity: High
Advisory: GHSA-vx9j-rvmj-jc32
CVE: CVE-2017-3200
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vx9j-rvmj-jc32
Type: github-advisory

## Affected
- Maven: `org.graniteds:granite-server-core` — affected >=0

## Details
The Java implementation of AMF3 deserializers used in GraniteDS, version 3.1.1.GA, may allow instantiation of arbitrary classes via their public parameter-less constructor and subsequently call arbitrary Java Beans setter methods. The ability to exploit this vulnerability depends on the availability of classes in the class path that make use of deserialization. A remote attacker with the ability to spoof or control information may be able to send serialized Java objects with pre-set properties that result in arbitrary code execution when deserialized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3200
- https://codewhitesec.blogspot.com/2017/04/amf.html
- https://github.com/graniteds/graniteds
- https://web.archive.org/web/20210124021547/http://www.securityfocus.com/bid/97382
- https://www.kb.cert.org/vuls/id/307983
- http://www.securityweek.com/flaws-java-amf-libraries-allow-remote-code-execution
