# [C] FreePBX api module Command Injection via GraphQL

## Summary
Severity: Critical
Advisory: CVE-2026-40520
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40520
Type: osv

## Details
FreePBX api module version 17.0.8 and prior contain a command injection vulnerability in the initiateGqlAPIProcess() function where GraphQL mutation input fields are passed directly to shell_exec() without sanitization or escaping. An authenticated user with a valid bearer token can send a GraphQL moduleOperations mutation with backtick-wrapped commands in the module field to execute arbitrary commands on the underlying host as the web server user.

## References
- https://github.com/FreePBX/api/blob/5f194e39a47e5481e8947f9694304d32724175f6/Api.class.php#L546C1-L554C3
- https://github.com/FreePBX/api/blob/5f194e39a47e5481e8947f9694304d32724175f6/ApiGqlHelper.class.php#L34C1-L36C136
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40520.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40520
- https://www.vulncheck.com/advisories/freepbx-api-module-command-injection-via-graphql
- https://github.com/FreePBX/api/commit/5f194e39a47e5481e8947f9694304d32724175f6
- https://github.com/FreePBX/api
