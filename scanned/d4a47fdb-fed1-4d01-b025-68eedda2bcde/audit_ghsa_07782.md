# [H] Statamic CMS vulnerable to privilege escalation via stored cross-site scripting

## Summary
Severity: High
Advisory: GHSA-ff9r-ww9c-43x8
CVE: CVE-2026-25759
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-ff9r-ww9c-43x8
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=6.0.0 <6.2.3

## Details
### Impact
Stored XSS vulnerability in content titles allow authenticated users with content creation permissions to inject malicious JavaScript that executes when viewed by higher-privileged users.

Malicious user must have an account with control panel access and content creation permissions.

This vulnerability can be exploited to allow super admin accounts to be created.

### Patches
This has been fixed in 6.2.3.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-ff9r-ww9c-43x8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25759
- https://github.com/statamic/cms/commit/6ed4f65f3387686d6dbd816e9b4f18a8d9736ff6
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v6.2.3
