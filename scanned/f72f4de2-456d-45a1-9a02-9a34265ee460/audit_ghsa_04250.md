# [C] OpenDJ Pre-Auth RCE via Java Deserialization in JMX RMI

## Summary
Severity: Critical
Advisory: GHSA-43x2-g84q-fmqx
CVE: CVE-2026-46495
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-43x2-g84q-fmqx
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.opendj:opendj-server-legacy` — affected >=0 <5.1.1

## Details
## Summary

**Description**

A Deserialization of Untrusted Data (CWE-502) issue in OpenDJ's JMX RMI connector allows an unauthenticated remote attacker to deserialize arbitrary Java objects on the server. The vulnerability exists because the platform reads and processes attacker-controlled bytes prior to authentication. This affects OpenDJ Community Edition through 5.1.0. This has been patched in version 5.1.1.

## Impact
This impacts all current OpenDJ releases where the JMX Connection Handler is enabled. While disabled by default, it is frequently enabled in practice for monitoring integrations. Exploitation requires TCP reachability to the configured listener and does not require authentication, prior privileges, or client certificates. Successful exploitation results in unauthenticated Remote Code Execution (RCE), with the severity depending on the runtime classpath and Java version. Unauthenticated RCE was demonstrated on the OpenDJ 4.4.15 (JDK 11 + Jackson 2.12.6.1).

## Patch
This has been patched in OpenDJ Community Edition version 5.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenDJ/security/advisories/GHSA-43x2-g84q-fmqx
- https://github.com/OpenIdentityPlatform/OpenDJ
