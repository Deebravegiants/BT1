# [H] OpenAM has Unsafe Java Deserialization via SNS

## Summary
Severity: High
Advisory: GHSA-pp89-732f-3g8q
CVE: CVE-2026-45794
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-pp89-732f-3g8q
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-push-notification` — affected >=0 <16.1.1

## Details
## Summary

**Description**

A Deserialization of Untrusted Data (CWE-502) issue exists in OpenAM's Push Notification SNS callback resource. The REST route that handles SNS push messages is mounted with anonymous access and, when a supplied message identifier has expired from the in-memory dispatcher, falls back to a CTS-stored predicate blob whose top-level keys are treated as Java class names and passed to Class.forName(...) before attacker-controlled JSON is deserialized via Jackson. This impacts OpenAM Community Edition through version 16.0.6. This issue was patched in version 16.1.1.

Arbitrary attacker-controlled code execution was not confirmed on tested stock classpaths for the latest release, but the flaw yields a reliable class-loading and Jackson-construction primitive whose impacts include remotely triggerable process execution, file writes, and DoS, depending on the deployment's classpath and environment.

## Impact
OpenAM Community Edition deployments through version 16.0.6 that enable the Push Notification Service with SNS callbacks are potentially affected. While the callback route itself is anonymous, the planting step requires a low-privileged user who can start Push Registration and read their own QR-code payload. After that user obtains the server-issued messageId, shared secret, and challenge, they can wait for the in-memory dispatcher entry to expire and then send anonymous SNS callbacks that overwrite the persistent CTS blob with attacker-controlled JSON. A later anonymous callback for the same messageId causes OpenAM to load an attacker-named class and construct it with attacker-controlled values.

The planted blob is processed server-side with internal CTS privileges, giving a reliable class-loading and Jackson-construction primitive that can corrupt the push-token record and trigger classpath-dependent side effects in the OpenAM JVM. Arbitrary attacker-controlled command execution was not confirmed on the tested stock classpaths; practical severity depends on enabled Push Registration flows, JDK version, bundled or co-deployed classes, and whether any reachable class-loading or construction side effects are security-relevant in the deployment.

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-pp89-732f-3g8q
- https://github.com/OpenIdentityPlatform/OpenAM
