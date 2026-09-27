# [M] Ratpack's default client side session signing key is highly predictable

## Summary
Severity: Medium
Advisory: GHSA-2cc5-23r7-vc4v
CVE: CVE-2021-29480
CWE: CWE-330, CWE-340
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-07-01
Source: https://github.com/advisories/GHSA-2cc5-23r7-vc4v
Type: github-advisory

## Affected
- Maven: `io.ratpack:ratpack-session` — affected >=0 <1.9.0

## Details
### Impact

The client side session module uses the application startup time as the signing key by default. This means that if an attacker can determine this time, and if encryption is not also used (which is recommended, but is not on by default), the session data could be tampered with by someone with the ability to write cookies. 

The default configuration is unsuitable for production use as an application restart renders all sessions invalid and is not multi-host compatible, but its use is not actively prevented.

### Vulnerability Location

https://github.com/ratpack/ratpack/blob/29434f7ac6fd4b36a4495429b70f4c8163100332/ratpack-session/src/main/java/ratpack/session/clientside/ClientSideSessionConfig.java#L29

### Patches

As of Ratpack 1.9.0 the default value is a securely randomly generated value, generated at application startup time. 

### Workarounds

Supply an alternative signing key, as per the documentation's recommendation.

## References
- https://github.com/ratpack/ratpack/security/advisories/GHSA-2cc5-23r7-vc4v
- https://nvd.nist.gov/vuln/detail/CVE-2021-29480
- https://github.com/ratpack/ratpack
- https://github.com/ratpack/ratpack/blob/29434f7ac6fd4b36a4495429b70f4c8163100332/ratpack-session/src/main/java/ratpack/session/clientside/ClientSideSessionConfig.java#L29
