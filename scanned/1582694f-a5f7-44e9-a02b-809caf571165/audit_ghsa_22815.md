# [H] GraniteDS Insecure Deserialization

## Summary
Severity: High
Advisory: GHSA-8m35-r25c-qr56
CVE: CVE-2017-3199
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8m35-r25c-qr56
Type: github-advisory

## Affected
- Maven: `org.graniteds:granite-core` — affected >=0

## Details
The Java implementation of GraniteDS, version 3.1.1.GA, AMF3 deserializers derives class instances from java.io.Externalizable rather than the AMF3 specification's recommendation of flash.utils.IExternalizable. A remote attacker with the ability to spoof or control an RMI server connection may be able to send serialized Java objects that execute arbitrary code when deserialized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3199
- https://codewhitesec.blogspot.com/2017/04/amf.html
- https://github.com/graniteds/graniteds
- https://web.archive.org/web/20210124021547/http://www.securityfocus.com/bid/97382
- https://www.kb.cert.org/vuls/id/307983
- http://www.securityweek.com/flaws-java-amf-libraries-allow-remote-code-execution
