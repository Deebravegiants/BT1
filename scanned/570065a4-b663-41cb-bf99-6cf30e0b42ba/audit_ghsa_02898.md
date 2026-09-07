# [C] Critical vulnerability found in cron-utils

## Summary
Severity: Critical
Advisory: GHSA-p9m8-27x8-rg87
CVE: CVE-2021-41269
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-15
Source: https://github.com/advisories/GHSA-p9m8-27x8-rg87
Type: github-advisory

## Affected
- Maven: `com.cronutils:cron-utils` — affected >=0 <9.1.6

## Details
### Impact
A Template Injection was identified in cron-utils enabling attackers to inject arbitrary Java EL expressions, leading to unauthenticated Remote Code Execution (RCE) vulnerability. Versions up to 9.1.2 are susceptible to this vulnerability. Please note, that only projects using the @Cron annotation to validate untrusted Cron expressions are affected.

### Patches
The issue was patched and a new version was released. Please upgrade to version 9.1.6.

### Workarounds
There are no known workarounds up to this moment.

### References
A description of the issue is provided in [issue 461](https://github.com/jmrozanec/cron-utils/issues/461)

### For more information
If you have any questions or comments about this advisory:

Open an issue in the [cron-utils Github repository](https://github.com/jmrozanec/cron-utils)

## References
- https://github.com/jmrozanec/cron-utils/security/advisories/GHSA-p9m8-27x8-rg87
- https://nvd.nist.gov/vuln/detail/CVE-2021-41269
- https://github.com/jmrozanec/cron-utils/issues/461
- https://github.com/jmrozanec/cron-utils/commit/cfd2880f80e62ea74b92fa83474c2aabdb9899da
- https://github.com/jmrozanec/cron-utils/commit/d6707503ec2f20947f79e38f861dba93b39df9da
- https://github.com/jmrozanec/cron-utils
