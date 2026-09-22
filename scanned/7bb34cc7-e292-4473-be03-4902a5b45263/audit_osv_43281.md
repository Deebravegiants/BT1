# [C] Activepieces: Remote Code Execution via Command Injection in Code Step Name

## Summary
Severity: Critical
Advisory: CVE-2026-73081
Aliases: GHSA-3pfv-m69p-5fv5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73081
Type: osv

## Details
Activepieces is an open source AI workflow automation platform. Prior to 0.80.0, the worker's code-compilation pipeline builds the on-disk path for a Code step from the step's name and passes that path to a shell-invoked build command. A step name containing shell metacharacters can break out of the intended build invocation and execute arbitrary commands during compilation before any code sandbox is created. An authenticated user with permission to create or edit a flow can execute commands as the worker process user, read and write the worker filesystem, exfiltrate environment secrets, and reach internal services available to the worker. This issue is fixed in version 0.80.0.

## References
- https://github.com/activepieces/activepieces/releases/tag/0.80.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73081.json
- https://github.com/activepieces/activepieces/security/advisories/GHSA-3pfv-m69p-5fv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-73081
