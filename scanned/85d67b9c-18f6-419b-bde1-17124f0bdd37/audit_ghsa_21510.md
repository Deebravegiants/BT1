# [H] Password exposure in H2 Database 

## Summary
Severity: High
Advisory: GHSA-22wj-vf5f-wrvj
CVE: CVE-2022-45868
CWE: CWE-200, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-23
Source: https://github.com/advisories/GHSA-22wj-vf5f-wrvj
Type: github-advisory

## Affected
- Maven: `com.h2database:h2` — affected >=1.4.198 <2.2.220

## Details
The web-based admin console in H2 Database Engine through 2.1.214 can be started via the CLI with the argument -webAdminPassword, which allows the user to specify the password in cleartext for the web admin console. Consequently, a local user (or an attacker that has obtained local access through some means) would be able to discover the password by listing processes and their arguments. NOTE: the vendor states "This is not a vulnerability of H2 Console ... Passwords should never be passed on the command line and every qualified DBA or system administrator is expected to know that."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45868
- https://github.com/h2database/h2database/issues/3686
- https://github.com/h2database/h2database/pull/3833
- https://github.com/h2database/h2database/commit/581ed18ff9d6b3761d851620ed88a3994a351a0d
- https://github.com/advisories/GHSA-22wj-vf5f-wrvj
- https://github.com/h2database/h2database
- https://github.com/h2database/h2database/blob/96832bf5a97cdc0adc1f2066ed61c54990d66ab5/h2/src/main/org/h2/server/web/WebServer.java#L346-L347
- https://github.com/h2database/h2database/releases/tag/version-2.2.220
- https://sites.google.com/sonatype.com/vulnerabilities/sonatype-2022-6243
