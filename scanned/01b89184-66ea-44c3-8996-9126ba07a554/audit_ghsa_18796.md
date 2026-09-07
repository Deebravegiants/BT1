# [H] Statamic Vulnerable to Superadmin Account Takeover via Stored Cross-Site Scripting and Lack of Proper X-CSRF-TOKEN Server-Side Validation

## Summary
Severity: High
Advisory: GHSA-g59r-24g3-h7cm
CVE: CVE-2025-64112
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-30
Source: https://github.com/advisories/GHSA-g59r-24g3-h7cm
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.22.1

## Details
### Impact

Stored XSS vulnerabilities in Collections and Taxonomies allow authenticated users with content creation permissions to inject malicious JavaScript that executes when viewed by higher-privileged users.

This affects:

- Control panel users with permission to create or edit Collections and Taxonomies
- Versions up to and including 5.22.0

The vulnerability can be exploited to:

- Change a super admin's password (versions ≤ 5.21.0)
- Change a super admin's email address to initiate password reset (version 5.22.0)
- Gain unauthorized access to superadmin accounts

The attack requires:

- An authenticated user with control panel and content creation permissions
- A super admin to view the compromised content

### Patches

This has been fixed in 5.22.1.

### Credits

Statamic thanks [Wojtek Chwala](https://github.com/wojtekchwala) for responsibly reporting the identified issues and working with us as we addressed them.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-g59r-24g3-h7cm
- https://nvd.nist.gov/vuln/detail/CVE-2025-64112
- https://github.com/statamic/cms/commit/e513751f433679ce698606e20c554a0c839987c1
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.22.1
