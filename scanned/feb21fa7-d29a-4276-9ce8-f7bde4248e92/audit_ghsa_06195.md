# [H] Craft CMS: Authenticated RCE via `condition.config` JSON cleanse bypass

## Summary
Severity: High
Advisory: GHSA-265m-7826-wjqm
CVE: CVE-2026-72778
CWE: CWE-915
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-265m-7826-wjqm
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.6
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.18.2

## Details
Craft CMS has an authenticated remote code execution issue in the control panel element-search condition handling.

Craft cleans the outer request-controlled condition array with `Component::cleanseConfig()`, but `Conditions::createCondition()` later decodes and merges the JSON string in `condition.config` without re-running `cleanseConfig()` on the decoded/merged configuration.

Because `condition.config` is a JSON string during the first cleanse, Yii special config keys such as `as` ... and `on` ... can be hidden inside it. After JSON decoding, those keys reach FieldLayout object creation and are interpreted by Yii as behavior/event configuration.

The RCE is semi-blind: the trigger endpoint returns a normal JSON response, and the command output is verified via a server-side file-write side effect retrieved in a subsequent request.

## Preconditions

- The attacker needs an authenticated Craft control panel session.
- A valid CSRF token is required.

## Impact

An authenticated control panel user can inject Yii behavior/event configuration after Craft’s intended config cleanse boundary. In the confirmed local lab, this led to command execution as the PHP/web user.

Potential attacker impact:
- Execute operating system commands as the PHP/web user.
- Read Craft secrets, environment variables, and application configuration.
- Access database credentials and stored site content.
- Modify site content, users, and application state.
- Pivot to internal services reachable from the Craft host or container.
- Cause denial of service or establish persistence depending on deployment permissions.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-265m-7826-wjqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-72778
- https://github.com/craftcms/cms/commit/353b5d676c88a854c9f6409ad83b837ca0c0e8da
- https://github.com/craftcms/cms/commit/789789dc9e2a4e2f2562f51aaf879fb7757d8340
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.18.2
- https://github.com/craftcms/cms/releases/tag/5.10.6
- https://www.vulncheck.com/advisories/craft-cms-rc1-before-authenticated-rce-via-condition-config
