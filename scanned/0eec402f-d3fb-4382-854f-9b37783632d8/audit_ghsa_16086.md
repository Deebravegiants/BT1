# [H] Ant-Media-Server vulnerable to Improper Output Neutralization for Logs

## Summary
Severity: High
Advisory: GHSA-2gx6-qrpp-c4p3
CVE: CVE-2024-35371
CWE: CWE-125
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-29
Source: https://github.com/advisories/GHSA-2gx6-qrpp-c4p3
Type: github-advisory

## Affected
- Maven: `io.antmedia:ant-media-server` — affected >=0 <2.9.0

## Details
Ant-Media-Server v2.8.2 is affected by Improper Output Neutralization for Logs. The vulnerability stems from insufficient input sanitization in the logging mechanism. Without proper filtering or validation, user-controllable data, such as identifiers or other sensitive information, can be included in log entries without restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-35371
- https://github.com/ant-media/ant-media-server/commit/4d4763bd4fd06e515c19544e5170ca0f34c9ce45
- https://gist.github.com/1047524396/4eb17867f2e375f4824274c5e7b4d384
- https://github.com/ant-media/Ant-Media-Server
- https://github.com/ant-media/Ant-Media-Server/blob/ams-v2.8.2/src/main/java/io/antmedia/rest/RestServiceBase.java#L356
