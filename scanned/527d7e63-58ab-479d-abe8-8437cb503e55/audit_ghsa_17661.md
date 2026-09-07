# [M] Para Inserts Sensitive Information into Log File for Facebook authentication

## Summary
Severity: Medium
Advisory: GHSA-qx7g-fx8q-545g
CVE: CVE-2025-49009
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-06
Source: https://github.com/advisories/GHSA-qx7g-fx8q-545g
Type: github-advisory

## Affected
- Maven: `com.erudika:para-server` — affected >=0 <1.50.8

## Details
CWE ID: CWE-532 (Insertion of Sensitive Information into Log File)
CVSS: 6.2 (Medium)
Vector: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N

**Affected Component:** Facebook Authentication Logging
**Version:** Para v1.50.6
**File Path:** para-1.50.6/para-server/src/main/java/com/erudika/para/server/security/filters/FacebookAuthFilter.java
**Vulnerable Line(s):** Line 184 (logger.warn(...) with raw access token)

Technical Details:

The vulnerability is located in FacebookAuthFilter.java, where a failed request to Facebook’s user profile endpoint triggers the following log statement:
```java
logger.warn("Facebook auth request failed: GET " + PROFILE_URL + accessToken, e);`
```

Here, `PROFILE_URL` is a constant:
```java
private static final String PROFILE_URL = "https://graph.facebook.com/me?fields=name,email,picture.width(400).type(square).height(400)&access_token=";
```
This results in the full request URL being logged, including the user's access token in plain text. Since WARN-level logs are often retained in production and accessible to operators or log aggregation systems, this poses a risk of token exposure.

## References
- https://github.com/Erudika/para/security/advisories/GHSA-qx7g-fx8q-545g
- https://nvd.nist.gov/vuln/detail/CVE-2025-49009
- https://github.com/Erudika/para/commit/46a908d887da02037384193f70a69345f04887cf
- https://github.com/Erudika/para
