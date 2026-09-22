# [M] Statamic CMS exposes two-factor recovery codes through dynamic Antlers rendering

## Summary
Severity: Medium
Advisory: GHSA-jppw-r5j3-xf7x
CVE: CVE-2026-71293
CWE: CWE-200, CWE-522
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-jppw-r5j3-xf7x
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1

## Details
Statamic CMS's user-augmentation resolver, AugmentedUser::get() in src/Auth/AugmentedUser.php, contains an explicit case for the `two_factor_recovery_codes` handle that returns the user's raw two-factor recovery codes with no access restriction: `if ($handle === 'two_factor_recovery_codes') { return new Value($this->data->get('two_factor_recovery_codes'), ...); }`. Unlike sensitive fields such as password/password_hash, which are excluded from AugmentedUser entirely, two_factor_recovery_codes is neither excluded from augmentation nor present in Statamic's Antlers variable guard lists (guardedVariablePatterns/guardedContentVariablePatterns in src/Providers/ViewServiceProvider.php, and the runtime GlobalRuntimeState guard paths), which by default only guard config.app.key. On any Antlers template field where raw/dynamic template rendering is enabled for a given field (an admin/developer-configured, blueprint-level field option), a template such as `{{ current_user.two_factor_recovery_codes }}{{ value }}|{{ /current_user.two_factor_recovery_codes }}` renders the viewing user's own 2FA recovery codes directly into the HTML response, allowing an attacker who can view or capture that response (e.g. via a shared/observable page, or a crafted link causing a victim to render it) to obtain the codes and bypass 2FA. Exploitation requires that dynamic Antlers rendering already be enabled on a field the target user's data flows through, which is a blueprint-configuration privilege rather than a standard content-editing permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-71293
- https://github.com/statamic/cms
- https://github.com/statamic/cms/blob/master/src/Auth/AugmentedUser.php
