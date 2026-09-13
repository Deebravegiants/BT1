# [H] Craft CMS vulnerable to behavior injection RCE via EntryTypesController

## Summary
Severity: High
Advisory: GHSA-qx2q-q59v-wf3j
CVE: CVE-2026-32263
CWE: CWE-470
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-qx2q-q59v-wf3j
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.6.0 <5.9.11

## Details
The fix for GHSA-7jx7-3846-m7w7 (commit 395c64f0b80b507be1c862a2ec942eaacb353748) only patched `src/services/Fields.php`, but the same vulnerable pattern exists in `EntryTypesController::actionApplyOverrideSettings()`.

In `src/controllers/EntryTypesController.php` lines 381-387:

```php
$settingsStr = $this->request->getBodyParam('settings');
parse_str($settingsStr, $postedSettings);
$settingsNamespace = $this->request->getRequiredBodyParam('settingsNamespace');
$settings = array_filter(ArrayHelper::getValue($postedSettings, $settingsNamespace, []));

if (!empty($settings)) {
    Craft::configure($entryType, $settings);
```

The `$settings` array from `parse_str` is passed directly to `Craft::configure()` without `Component::cleanseConfig()`. This allows injecting Yii2 behavior/event handlers via `as ` or `on ` prefixed keys, the same attack vector as the original advisory.

You need Craft control panel administrator permissions, and `allowAdminChanges` must be enabled for this to work.

An attacker can use the same gadget chain from the original advisory to achieve RCE.

Users should update to Craft 5.9.11 to mitigate the issue.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-7jx7-3846-m7w7
- https://github.com/craftcms/cms/security/advisories/GHSA-qx2q-q59v-wf3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-32263
- https://github.com/craftcms/cms/commit/d37389dbffafa565143be40a2ab1e1db22a863f7
- https://github.com/craftcms/cms
