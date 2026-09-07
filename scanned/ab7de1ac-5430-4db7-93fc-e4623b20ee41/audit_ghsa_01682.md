# [H] Improper Validation of Certificate with Host Mismatch in Java-WebSocket

## Summary
Severity: High
Advisory: GHSA-gw55-jm4h-x339
CVE: CVE-2020-11050
CWE: CWE-295, CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-08
Source: https://github.com/advisories/GHSA-gw55-jm4h-x339
Type: github-advisory

## Affected
- Maven: `org.java-websocket:Java-WebSocket` — affected >=0 <1.5.0

## Details
The Java-WebSocket Client does not perform hostname verification.

 - This means that SSL certificates of other hosts are accepted as long as they are trusted. To exploit this vulnerability an attacker has to perform a man-in-the-middle (MITM) attack between a Java application using the Java-WebSocket Client and an WebSocket server it's connecting to.
 - TLS normally protects users and systems against MITM attacks, it cannot if certificates from other trusted hosts are accepted by the client.

For more information see: CWE-297: Improper Validation of Certificate with Host Mismatch - https://cwe.mitre.org/data/definitions/297.html

## Important note

The OWASP Dependency-Check (https://jeremylong.github.io/DependencyCheck/index.html) may report that a dependency of your project is affected by this security vulnerability, but you don't use this lib.
This is caused by the fuzzy search in the OWASP implementation.
Check out this issue (https://github.com/TooTallNate/Java-WebSocket/issues/1019#issuecomment-628507934) for more information and a way to suppress the warning.

## References
- https://github.com/TooTallNate/Java-WebSocket/security/advisories/GHSA-gw55-jm4h-x339
- https://nvd.nist.gov/vuln/detail/CVE-2020-11050
- https://github.com/TooTallNate/Java-WebSocket
