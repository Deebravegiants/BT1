# [H] Symfony vulnerable to command execution hijack on Windows with Process class

## Summary
Severity: High
Advisory: GHSA-qq5c-677p-737q
CVE: CVE-2024-51736
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-06
Source: https://github.com/advisories/GHSA-qq5c-677p-737q
Type: github-advisory

## Affected
- Packagist: `symfony/process` — affected >=0 <5.4.46
- Packagist: `symfony/process` — affected >=6.0.0 <6.4.14
- Packagist: `symfony/process` — affected >=7.0.0 <7.1.7
- Packagist: `symfony/symfony` — affected >=0 <5.4.46
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.14
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.1.7

## Details
### Description

On Windows, when an executable file named `cmd.exe` is located in the current working directory it will be called by the `Process` class when preparing command arguments, leading to possible hijacking.

### Resolution

The `Process` class now uses the absolute path to `cmd.exe`.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/18ecd03eda3917fdf901a48e72518f911c64a1c9) for branch 5.4.

### Credits

We would like to thank Jordi Boggiano for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-qq5c-677p-737q
- https://nvd.nist.gov/vuln/detail/CVE-2024-51736
- https://github.com/symfony/symfony/commit/18ecd03eda3917fdf901a48e72518f911c64a1c9
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/process/CVE-2024-51736.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2024-51736.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2024-51736
