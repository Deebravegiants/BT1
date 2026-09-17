# [H] Cachet vulnerable to new line injection during configuration edition

## Summary
Severity: High
Advisory: GHSA-9jxw-cfrh-jxq6
CVE: CVE-2021-39172
CWE: CWE-93
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-9jxw-cfrh-jxq6
Type: github-advisory

## Affected
- Packagist: `cachethq/cachet` — affected >=0 <2.5.1

## Details
### Impact

Authenticated users, regardless of their privileges (_User_ or _Admin_), can exploit a new line injection in the configuration edition feature (e.g. mail settings) and gain arbitrary code execution on the server.

### Patches

This issue was addressed by improving `UpdateConfigCommandHandler` and preventing the use of new lines characters in new configuration values.

### Workarounds

Only allow trusted source IP addresses to access to the administration dashboard.

### References

- https://blog.sonarsource.com/cachet-code-execution-via-laravel-configuration-injection

### For more information

If you have any questions or comments about this advisory, you can contact:
- The original reporters, by sending an email to vulnerability.research [at] sonarsource.com;
- The maintainers, by opening an issue on this repository.

## References
- https://github.com/fiveai/Cachet/security/advisories/GHSA-9jxw-cfrh-jxq6
- https://nvd.nist.gov/vuln/detail/CVE-2021-39172
- https://github.com/fiveai/Cachet/commit/6442976c25930cb370c65a22784b9caee7ed1de2
- https://blog.sonarsource.com/cachet-code-execution-via-laravel-configuration-injection
- https://github.com/fiveai/Cachet
- https://github.com/fiveai/Cachet/releases/tag/v2.5.1
