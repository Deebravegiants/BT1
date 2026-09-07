# [C] ConsoleMe has an Arbitrary File Read Vulnerability via Limited Git command

## Summary
Severity: Critical
Advisory: GHSA-3783-62vc-jr7x
CVE: CVE-2024-5023
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-16
Source: https://github.com/advisories/GHSA-3783-62vc-jr7x
Type: github-advisory

## Affected
- PyPI: `consoleme` — affected >=0 <1.4.0

## Details
## ID: NFLX-2024-002

### Impact
Authenticated users can achieve limited RCE in ConsoleMe, restricted to flag inputs on a single CLI command. Due to this constraint, it is not currently known whether full RCE is possible but it is unlikely. 
However, a specific flag allows authenticated users to read any server files accessible by the ConsoleMe process. Given ConsoleMe's role as an AWS identity broker, accessing files containing secrets on the server could potentially be exploited for privilege escalation.

Deployments of ConsoleMe that allow templated resources are impacted and urged to patch immediately. Deployments that do not permit templated resources are not affected.

To determine if your ConsoleMe deployment uses templated resources, check the configuration value for `cache_resource_templates.repositories`. If this value does not exist or is an empty array, your deployment is not impacted.
### Description
The self-service flow for templated resources in ConsoleMe accepts a user-supplied JSON post body, which includes the filename for the templated resource. However, this user-supplied filename is not properly sanitized and is passed directly as a string to a CLI command. This allows users to input flags instead of filenames. By passing a specific flag with a filename value, users can induce an error that reveals the contents of the specified file, allowing them to read any files readable by the system user executing the ConsoleMe server process.

### Patches
This issue has been patched in version [v1.4.0](https://pypi.org/project/consoleme/1.4.0/) via https://github.com/Netflix/consoleme/pull/9380. 
If you are unable to upgrade to the latest version, users can selectively apply the code changes in the above PR. Alternatively, removing the configuration item `cache_resource_templates.repositories` or adding it as an empty array should mitigate the issue, but will result in broken functionality (templated resources will no longer be supported for self-service).

### Credit
[Jay Dhulia](https://github.com/jaydhulia)

## References
- https://github.com/Netflix/consoleme/security/advisories/GHSA-3783-62vc-jr7x
- https://nvd.nist.gov/vuln/detail/CVE-2024-5023
- https://github.com/Netflix/consoleme/pull/9380
- https://github.com/Netflix/consoleme/commit/2795a2bd553938a21c0643b37452971625ce67f5
- https://github.com/Netflix/consoleme
- https://github.com/Netflix/security-bulletins/blob/master/advisories/nflx-2024-002.md
