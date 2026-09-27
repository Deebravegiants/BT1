# [H] Authenticated Rundeck users can view or delete jobs they do not have authorization for.

## Summary
Severity: High
Advisory: GHSA-phmw-jx86-x666
CVE: CVE-2023-48222
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-phmw-jx86-x666
Type: github-advisory

## Affected
- Maven: `org.rundeck:rundeck` — affected >=4.12.0 <4.17.3

## Details
Access to two URLs used in both Rundeck Open Source and Process Automation products could allow authenticated users to access the URL path, which would allow access to view or delete jobs, without the necessary authorization checks.

The affected URLs are:
- `http[s]://[host]/context/rdJob/*` 
- `http[s]://[host]/context/api/*/incubator/jobs`

### Impact

Rundeck, Process Automation version 4.12.0 up to 4.16.0

### Patches

Patched versions: 4.17.3

### Workarounds

Access to two URLs used in either Rundeck Open Source or Process Automation products could be blocked at a load balancer level.
- `http[s]://host/context/rdJob/*` 
- `http[s]://host/context/api/*/incubator/jobs`

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [our forums](https://community.pagerduty.com/forum/c/process-automation)
* Enterprise Customers can open a [Support ticket](https://support.rundeck.com)

## References
- https://github.com/rundeck/rundeck/security/advisories/GHSA-phmw-jx86-x666
- https://nvd.nist.gov/vuln/detail/CVE-2023-48222
- https://github.com/rundeck/rundeck
