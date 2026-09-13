# [M] Winter: SQL Injection in Backend Filter Widget numberrange Scope via numbersFromAjax

## Summary
Severity: Medium
Advisory: GHSA-m7jc-g4rc-jmvh
CVE: CVE-2026-32593
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-m7jc-g4rc-jmvh
Type: github-advisory

## Affected
- Packagist: `winter/wn-backend-module` — affected >=0 <1.2.13

## Details
## Impact

The Backend Filter widget (`Backend\Widgets\Filter`) is vulnerable to SQL injection through the `numberrange` scope type when the scope is configured with a `conditions` key. An authenticated backend user with access to a list view containing a vulnerable filter scope can inject arbitrary SQL via the filter's AJAX handler, potentially gaining read access to the full database contents.

To exploit this, an attacker must have a valid backend account with access to a list view where a third-party plugin has registered a `numberrange` filter scope using the `conditions` configuration key. No built-in Winter CMS backend views use this scope type and configuration combination, so a vanilla installation without plugins is not exploitable.

## Patches

This issue has been fixed in Winter CMS v1.2.13.

## Workarounds

If users cannot upgrade, they may apply commit https://github.com/wintercms/winter/commit/50713de95adf5298536d93f4d999652525d36d43 to your Winter CMS
installation manually to resolve this issue.

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-m7jc-g4rc-jmvh
- https://github.com/wintercms/winter/commit/50713de95adf5298536d93f4d999652525d36d43
- https://github.com/wintercms/winter
