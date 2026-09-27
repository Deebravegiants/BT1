# [M] MongoDB C# Driver Risk of Exposing Authentication Data via Command Listener

## Summary
Severity: Medium
Advisory: GHSA-p9rv-qgqw-jx2w
CVE: CVE-2021-20331
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p9rv-qgqw-jx2w
Type: github-advisory

## Affected
- NuGet: `mongodb.driver` — affected >=2.11.0 <2.12.2

## Details
Specific versions of the MongoDB C# Driver may erroneously publish events containing authentication-related data to a command listener configured by an application. The published events may contain security-sensitive data when commands such as "saslStart", "saslContinue", "isMaster", "createUser", and "updateUser" are executed. Without due care, an application may inadvertently expose this authenticated-related information, e.g., by writing it to a log file. This issue only arises if an application enables the command listener feature (this is not enabled by default). This issue affects the MongoDB C# Driver 2.12 <= 2.12.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20331
- https://github.com/mongodb/mongo-csharp-driver/commit/1f1a526e93ed7aa254759704b19f5ee66a3af365
- https://jira.mongodb.org/browse/CSHARP-3521
