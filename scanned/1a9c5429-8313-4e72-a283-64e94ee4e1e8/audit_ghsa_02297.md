# [H] Cachet configuration leak

## Summary
Severity: High
Advisory: GHSA-88f9-7xxh-c688
CVE: CVE-2021-39174
CWE: CWE-75
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-88f9-7xxh-c688
Type: github-advisory

## Affected
- Packagist: `cachethq/cachet` — affected >=0 <2.5.1

## Details
### Impact

Authenticated users, regardless of their privileges (_User_ or _Admin_), can leak the value of any configuration entry of the dotenv file, e.g. the application secret (`APP_KEY`) and various passwords (email, database, etc). 

### Patches

This issue was addressed by improving `UpdateConfigCommandHandler` and preventing the use of nested variables in the resulting dotenv configuration file.

### Workarounds

Only allow trusted source IP addresses to access to the administration dashboard.

### References

Further technical details are available at [https://blog.sonarsource.com/cachet-code-execution-via-laravel-configuration-injection](https://blog.sonarsource.com/cachet-code-execution-via-laravel-configuration-injection).

### For more information

If you have any questions or comments about this advisory, you can contact:
- The original reporters, by sending an email to vulnerability.research [at] sonarsource.com;
- The maintainers, by opening an issue on this repository.

## References
- https://github.com/fiveai/Cachet/security/advisories/GHSA-88f9-7xxh-c688
- https://nvd.nist.gov/vuln/detail/CVE-2021-39174
- https://blog.sonarsource.com/cachet-code-execution-via-laravel-configuration-injection
- https://github.com/cachethq/Cachet
- https://github.com/fiveai/Cachet/releases/tag/v2.5.1
