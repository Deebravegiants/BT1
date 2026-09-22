# [M] Authenticated users can view job names and groups they do not have authorization to view

## Summary
Severity: Medium
Advisory: GHSA-xvmv-4rx6-x6jx
CVE: CVE-2023-47112
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-xvmv-4rx6-x6jx
Type: github-advisory

## Affected
- Maven: `org.rundeck:rundeckapp` — affected >=4.17.0 <4.17.3

## Details
Access to two URLs used in both Rundeck Open Source and Process Automation products could allow authenticated users to access the URL path, which provides a list of job names and groups for any project, without the necessary authorization checks.

The affected URLs are:
- `http[s]://[host]/context/rdJob/*` 
- `http[s]://[host]/context/api/*/incubator/jobs`

The output of these endpoints only exposes the name of job groups and the jobs contained within the specified project.  The output is read-only and the access does not allow changes to the information.

### Impact

Rundeck, Process Automation version 4.17.0 up to 4.17.2

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
- https://github.com/rundeck/rundeck/security/advisories/GHSA-xvmv-4rx6-x6jx
- https://nvd.nist.gov/vuln/detail/CVE-2023-47112
- https://github.com/rundeck/rundeck/commit/8992879036a1ddacfca78559d823be0424796e7e
- https://github.com/rundeck/rundeck
