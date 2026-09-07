# [H] Pimcore ENV Variables and Cookie Informations are exposed in http_error_log

## Summary
Severity: High
Advisory: GHSA-q433-j342-rp9h
CVE: CVE-2026-23493
CWE: CWE-532
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-q433-j342-rp9h
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1 <12.3.1
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.14

## Details
### Summary
The http_error_log file stores the $_COOKIE and $_SERVER variables, which means sensitive information such as database passwords, cookie session data, and other details can be accessed or recovered through the Pimcore backend.

### Details
It’s better to remove both lines, as this information makes little sense in this context anyway.

https://github.com/pimcore/pimcore/blob/12.x/bundles/SeoBundle/src/EventListener/ResponseExceptionListener.php#L92
https://github.com/pimcore/pimcore/blob/12.x/bundles/SeoBundle/src/EventListener/ResponseExceptionListener.php#L93

### PoC
In the Pimcore backend, navigate to "Search Engine Optimization" and click on "HTTP Errors." Double-click on an entry to view its details. Here, you may find sensitive data exposed.

### Impact
Pimcore backend users can access sensitive environment variables, potentially exposing critical information.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-q433-j342-rp9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-23493
- https://github.com/pimcore/pimcore/pull/18918
- https://github.com/pimcore/pimcore/commit/002ec7d5f84973819236796e5b314703b58e8601
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v11.5.14
- https://github.com/pimcore/pimcore/releases/tag/v12.3.1
