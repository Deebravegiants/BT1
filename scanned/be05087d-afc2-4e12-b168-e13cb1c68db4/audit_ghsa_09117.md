# [C] Codechecker has an authentication bypass for certain API calls

## Summary
Severity: Critical
Advisory: GHSA-4v9x-cqc5-j645
CVE: CVE-2026-25660
CWE: CWE-290, CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-4v9x-cqc5-j645
Type: github-advisory

## Affected
- PyPI: `codechecker` — affected >=0

## Details
### Summary
Authentication bypass occurs when the URL ends with Authentication with certain function calls. This bypass allows assigning arbitrary permissions to any existing user in CodeChecker.

### Details

The following functions are affected under the Authentication endpoint: `getAuthorisedNames`, `getPermissionsForUser`, `hasPermission`, `addPermission`, and `removePermission`.

The vulnerability allows unauthenticated users to execute these function calls with arbitrary arguments.
In the logs, the exploit shows as follows:
```
[INFO 2026-04-23 21:23] - 127.0.0.1:42654 -- [Anonymous] POST /v6.67/Authentication@getAuthorisedNames
[INFO 2026-04-23 21:23] - 127.0.0.1:42654 -- [Anonymous] POST /v6.67/Authentication@addPermission
```

### Impact
An attacker with a CodeChecker user can effectively acquire superuser permissions by calling these endpoints.

### Patch
A patch is available at https://github.com/Ericsson/codechecker/releases/tag/v6.27.4.

## References
- https://github.com/Ericsson/codechecker/security/advisories/GHSA-4v9x-cqc5-j645
- https://nvd.nist.gov/vuln/detail/CVE-2026-25660
- https://github.com/Ericsson/codechecker
