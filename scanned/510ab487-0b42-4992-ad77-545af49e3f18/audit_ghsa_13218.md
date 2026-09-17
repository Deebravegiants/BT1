# [C] SQLpage vulnerable to public exposure of database credentials

## Summary
Severity: Critical
Advisory: GHSA-v5wf-jg37-r9m5
CVE: CVE-2023-42454
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-09-21
Source: https://github.com/advisories/GHSA-v5wf-jg37-r9m5
Type: github-advisory

## Affected
- crates.io: `sqlpage` — affected >=0 <0.11.1

## Details
### Impact

If
 - you are using a SQLPage version older than v0.11.1 
 - your SQLPage instance is exposed publicly
 - the database connection string is specified in the `sqlpage/sqlpage.json` configuration file (not in an environment variable)
 - the web_root is the current working directory (the default)
 - your database is exposed publicly

then an attacker could retrieve the database connection information from SQLPage and use it to connect to your database directly.

### Patches

Upgrade to [v0.11.1](https://github.com/lovasoa/SQLpage/releases/tag/v0.11.1) as soon as possible.

### Workarounds

If you cannot upgrade immediately:

 - Using an environment variable instead of the configuration file to specify the database connection string prevents exposing it on vulnerable versions.
 - Using a different [web root](https://github.com/lovasoa/SQLpage/blob/main/configuration.md) (that is not a parent of the SQLPage configuration directory) fixes the issue.
 - And in any case, you should generally avoid exposing your database publicly 

### References

https://github.com/lovasoa/SQLpage/issues/89

## References
- https://github.com/lovasoa/SQLpage/security/advisories/GHSA-v5wf-jg37-r9m5
- https://nvd.nist.gov/vuln/detail/CVE-2023-42454
- https://github.com/lovasoa/SQLpage/issues/89
- https://github.com/lovasoa/SQLpage
- https://github.com/lovasoa/SQLpage/releases/tag/v0.11.1
