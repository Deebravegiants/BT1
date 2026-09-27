# [H] Craft Commerce hasVariant/hasProduct Blind SQL Injection

## Summary
Severity: High
Advisory: GHSA-r54v-qq87-px5r
CVE: CVE-2026-32272
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-r54v-qq87-px5r
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.6.0

## Details
## Overview

Craft Commerce’s `ProductQuery::hasVariant` and `VariantQuery::hasProduct` properties bypass the `unset()` blocklist added to `ElementIndexesController` in GHSA-2453-mppf-46cj.

The blocklist only strips top-level Yii2 Query properties (`where`, `orderBy`, etc.), but `hasVariant` and `hasProduct` pass
through untouched. Internally, these properties call `Craft::configure()` on a subquery without sanitization, re-introducing SQL injection via `criteria[hasVariant][where]=INJECTED_SQL`.

An authenticated control panel user can perform boolean-based blind SQL injection through the patched `ElementIndexesController` and extract arbitrary database contents.

## Impact

* Full database read access via blind SQL injection
* Privilege escalation via security key extraction → forged admin sessions

## Prerequisites
* Authenticated control panel user
* Commerce plugin installed
* Products with variants in the database

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-r54v-qq87-px5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-32272
- https://github.com/craftcms/commerce/pull/4232
- https://github.com/advisories/GHSA-2453-mppf-46cj
- https://github.com/craftcms/commerce
- https://github.com/craftcms/commerce/releases/tag/5.6.0
