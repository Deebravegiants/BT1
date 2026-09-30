# [H] Cachet vulnerable to forced reinstall

## Summary
Severity: High
Advisory: GHSA-r67m-m8c7-jp83
CVE: CVE-2021-39173
CWE: CWE-704
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-r67m-m8c7-jp83
Type: github-advisory

## Affected
- Packagist: `cachethq/cachet` — affected >=0 <2.5.1

## Details
### Impact

Authenticated users, regardless of their privileges (_User_ or _Admin_), can trick Cachet and install the instance again, leading to arbitrary code execution on the server.

### Patches

This issue was addressed by improving the middleware `ReadyForUse`, which now performs a stricter validation of the instance name. 

### Workarounds

Only allow trusted source IP addresses to access to the administration dashboard.

### References

- https://blog.sonarsource.com/cachet-code-execution-via-laravel-configuration-injection

### For more information

If you have any questions or comments about this advisory, you can contact:
- The original reporters, by sending an email to vulnerability.research [at] sonarsource.com;
- The maintainers, by opening an issue on this repository.

## References
- https://github.com/fiveai/Cachet/security/advisories/GHSA-r67m-m8c7-jp83
- https://nvd.nist.gov/vuln/detail/CVE-2021-39173
- https://blog.sonarsource.com/cachet-code-execution-via-laravel-configuration-injection
- https://github.com/fiveai/Cachet
- https://github.com/fiveai/Cachet/releases/tag/v2.5.1
