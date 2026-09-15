# [M] Para Server Logs Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-v75g-77vf-6jjq
CVE: CVE-2025-48955
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-05-30
Source: https://github.com/advisories/GHSA-v75g-77vf-6jjq
Type: github-advisory

## Affected
- Maven: `com.erudika:para-server` — affected >=0 <1.50.8

## Details
CWE ID: CWE-532 (Insertion of Sensitive Information into Log File)
CVSS:  7.5 (High)
Vector: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N

**Affected Component:** Para Server Initialization Logging
**Version:** Para v1.50.6
**File Path:** `para-1.50.6/para-server/src/main/java/com/erudika/para/server/utils/HealthUtils.java`
**Vulnerable Line(s):** Line 132 (via `logger.info(...)` with root credentials)

Technical Details:

The vulnerability is located in the HealthUtils.java file, where a failed configuration file write triggers the following logging statement:
```java
logger.info("Initialized root app with access key '{}' and secret '{}', but could not write these to {}.",
    rootAppCredentials.get("accessKey"),
    rootAppCredentials.get("secretKey"),
    confFile);
```
This exposes both access and secret keys in logs without redaction. These credentials are later reused in variable assignments for persistence but do not require logging for debugging or system health purposes.

## References
- https://github.com/Erudika/para/security/advisories/GHSA-v75g-77vf-6jjq
- https://nvd.nist.gov/vuln/detail/CVE-2025-48955
- https://github.com/Erudika/para/commit/1e8a89558542854bb0683ab234c4429ad93b0835
- https://github.com/Erudika/para
