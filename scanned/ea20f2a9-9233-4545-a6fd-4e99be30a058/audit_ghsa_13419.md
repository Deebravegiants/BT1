# [C] Apache StreamPark Improper Input Validation vulnerability

## Summary
Severity: Critical
Advisory: GHSA-m5h8-2pjw-vg3j
CVE: CVE-2022-46365
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-m5h8-2pjw-vg3j
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=1.0.0 <2.0.0

## Details
Apache StreamPark 1.0.0 before 2.0.0 When the user successfully logs in, to modify his profile, the username will be passed to the server-layer as a parameter, but not verified whether the user name is the currently logged user and whether the user is legal, This will allow malicious attackers to send any username to modify and reset the account, Users of the affected versions should upgrade to Apache StreamPark 2.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46365
- https://github.com/apache/incubator-streampark/pull/2123
- https://github.com/apache/incubator-streampark/commit/4f39d7f422d7519a3febc2d15d31ed0126d54fbc
- https://github.com/apache/incubator-streampark
- https://github.com/apache/incubator-streampark/blob/dev/streampark-console/streampark-console-service/src/main/java/org/apache/streampark/console/system/controller/UserController.java#L128
- https://github.com/apache/incubator-streampark/blob/dev/streampark-console/streampark-console-service/src/main/java/org/apache/streampark/console/system/service/impl/UserServiceImpl.java#L149-L162
- https://lists.apache.org/thread/f68lcwrp8pcdc4yrbpcm8j7m0f5mjn7h
