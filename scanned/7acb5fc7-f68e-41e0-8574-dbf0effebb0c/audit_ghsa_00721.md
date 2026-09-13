# [H] Privilege escalation in Presto

## Summary
Severity: High
Advisory: GHSA-f6pc-crhh-cp96
CVE: CVE-2020-15087
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-06-30
Source: https://github.com/advisories/GHSA-f6pc-crhh-cp96
Type: github-advisory

## Affected
- Maven: `io.prestosql:presto-server` — affected >=0 <337

## Details
### Affected
This affects Presto server installations. This does NOT affect clients such as the CLI or JDBC driver.

### Impact
Authenticated users can bypass authorization checks by directly accessing internal APIs. This impacts Presto server installations with secure internal communication configured.

This does not affect installations that have not configured secure internal communication, as these installations are inherently insecure.

### Patches
This issue has been fixed starting with PrestoSQL version 337.

### Workarounds
This issue can be mitigated by blocking network access to internal APIs on the coordinator and workers. 

### References
See the Presto documentation for [Secure Internal Communication](https://trino.io/docs/current/security/internal-communication.html).

### For more information
If you have any questions or comments about this advisory:
* Join the **#security** channel on [Slack](https://trino.io/slack.html).
* Contact the security team at [security@trino.io](mailto:security@trino.io)

## References
- https://github.com/prestosql/presto/security/advisories/GHSA-f6pc-crhh-cp96
- https://github.com/trinodb/trino/security/advisories/GHSA-f6pc-crhh-cp96
- https://nvd.nist.gov/vuln/detail/CVE-2020-15087
- https://prestosql.io/docs/current/release/release-337.html#security-changes
- https://trino.io/docs/current/release/release-337.html#security-changes
