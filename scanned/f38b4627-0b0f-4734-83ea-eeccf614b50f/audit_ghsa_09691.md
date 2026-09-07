# [H] Craft Commerce has a SQL Injection can lead to Remote Code Execution via TotalRevenue Widget

## Summary
Severity: High
Advisory: GHSA-875v-7m49-8x88
CVE: CVE-2026-32271
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-875v-7m49-8x88
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=4.0.0 <4.10.3
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.5.5

## Details
## Summary

A SQL injection in the Commerce TotalRevenue widget can lead to remote code execution through a chain of four vulnerabilities:

* SQL Injection -- The TotalRevenue stat interpolates unsanitized widget settings directly into a sprintf-based SQL Expression.  Any control panel user can create any widget type without permission checks.

* PDO Multi-Statement Queries -- PHP `PDO MySQL` enables `CLIENT_MULTI_STATEMENTS` by default. Neither Yii2 nor Craft CMS disables it. This allows stacking an INSERT statement after the injected SELECT , writing a maliciously serialized PHP object into the queue table.

* Unrestricted `unserialize()` -- The yii2-queue PhpSerializer calls `unserialize()` with no allowed_classes restriction on every queue job. When the queue consumer processes the injected job, it instantiates the attacker-controlled object.

* Gadget Chain (FileCookieJar) -- `GuzzleHttp\Cookie\FileCookieJar` (a standard Guzzle dependency) has an unguarded `__destruct()` method that calls `file_put_contents()`. The attacker’s serialized payload writes a PHP webshell to the server’s webroot. PHP tags survive `json_encode()` because Guzzle uses `options=0` (no `JSON_HEX_TAG`).

The complete chain requires 3 HTTP requests and achieves arbitrary command execution as the PHP process user. Queue processing is triggered via GET `/actions/queue/run`, an endpoint that requires no authentication (`$allowAnonymous = ['run']`).

## RCE Exploitation Steps

* Authenticate as any control panel user
* POST to `/admin/actions/dashboard/create-widget` with stacked SQL injection:
* `settings[type]` contains the stacked INSERT with the serialized gadget chain
* Response: HTTP 500 (expected -- INSERT already committed)
* Trigger queue processing: `GET /actions/queue/run`
* Queue consumer deserializes the gadget chain
* `FileCookieJar::__destruct()` writes webshell to webroot
* Access the webshell: `GET /poc_rce.php?c=id`
* Response: `uid=1000(home) gid=1000(home) groups=1000(home)`

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-875v-7m49-8x88
- https://nvd.nist.gov/vuln/detail/CVE-2026-32271
- https://github.com/craftcms/commerce/commit/6d2d24b3a2b0c06593856d05446f82bd8af92d72
- https://github.com/craftcms/commerce
