# [H] Craft CMS: RCE via missing cleanseConfig in FieldsController::actionRenderCardPreview

## Summary
Severity: High
Advisory: GHSA-86vw-x4ww-x467
CVE: CVE-2026-56382
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-86vw-x4ww-x467
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.5.0 <5.9.14

## Details
The `actionRenderCardPreview()` method in `FieldsController` passes the `fieldLayoutConfig` POST parameter directly to `Fields::createLayout()` without calling `Component::cleanseConfig()`. This allows Yii2 event handler injection via `on eventName` keys in the config array, leading to arbitrary code execution.

This is the same vulnerability pattern that was fixed in GHSA-4484-8v2f-5748 (same file, `_fldComponent` method correctly uses `cleanseConfig`), GHSA-qx2q-q59v-wf3j (EntryTypesController), and GHSA-2fph-6v5w-89hh (ElementIndexesController).

## PoC

As an admin user with a valid session:

```
POST /admin/actions/fields/render-card-preview HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Cookie: CraftSessionId=<session>

fieldLayoutConfig[on+init]=phpinfo&CRAFT_CSRF_TOKEN=<token>
```

When the FieldLayout object is constructed, Yii2 processes the `on init` key as an event handler registration. During `Component::init()`, the `init` event is triggered, calling `phpinfo()`. The phpinfo output (which includes environment variables, potentially containing database credentials and `CRAFT_SECURITY_KEY`) will appear in the response.

## Impact

An authenticated admin can achieve RCE through Yii2 event handler injection. While this requires admin access (same as GHSA-4484-8v2f-5748, which was rated moderate), it allows arbitrary PHP function execution and information disclosure via phpinfo.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-86vw-x4ww-x467
- https://nvd.nist.gov/vuln/detail/CVE-2026-56382
- https://github.com/craftcms/cms
- https://www.vulncheck.com/advisories/craft-cms-remote-code-execution-via-missing-config-sanitization-in-fieldscontroller
