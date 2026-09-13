# [M] Bypass of CMS Safe Mode Security Feature

## Summary
Severity: Medium
Advisory: GHSA-q37h-jhf3-85cj
Ecosystem: Packagist
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-q37h-jhf3-85cj
Type: github-advisory

## Affected
- Packagist: `wintercms/winter` — affected >=0 <1.0.475
- Packagist: `wintercms/winter` — affected >=1.1.0 <1.1.9

## Details
### Impact

Authenticated users with permissions to create or modify theme template objects through the backend "CMS" editor can exploit this vulnerability to bypass the `cms.enableSafeMode` security feature if enabled (disables modification of PHP code through the web interface when enabled).

This is only an issue for Winter CMS instances that rely on the Safe Mode security feature to prevent privileged users from modifying the PHP code of CMS theme template objects through the web interface.

CVSS v3.1 Vector: [AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H/E:P/RL:O/RC:C](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H/E:P/RL:O/RC:C&version=3.1)

### Patches

Issue has been fixed in v1.0.475, v1.1.9, & v1.2. 

### Workarounds

Apply https://github.com/wintercms/storm/commit/03eb5ce3f2a271670574802b914f7bcaf07663c1 manually if unable to upgrade to v1.0.475, v1.1.9, or v1.2.0.

### References

See https://github.com/octobercms/october/security/advisories/GHSA-79jw-2f46-wv22/.

Credit to [David Miller](https://github.com/cydave) for reporting the issue.

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@wintercms.com](mailto:hello@wintercms.com)

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-q37h-jhf3-85cj
- https://github.com/wintercms/winter
