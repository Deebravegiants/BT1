# [M] Smarty Security stream restriction bypass through stream: resource

## Summary
Severity: Medium
Advisory: GHSA-rjhh-76wf-8xmw
CVE: CVE-2026-62996
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-rjhh-76wf-8xmw
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=5.0.0 <5.8.4

## Details
`smarty/smarty` version `5.8.0` can read local files through PHP stream wrappers even when Smarty Security is enabled and all streams are disabled with `Security::$streams = null`.

The bypass uses Smarty's built-in `stream:` resource type. A template such as:

```smarty
{include file="stream:php://filter/read=convert.base64-encode/resource=/tmp/secret.tpl"}
```

is handled as Smarty resource type `stream`, so the security check that would normally reject the underlying `php` wrapper is not applied. `StreamPlugin` then opens the nested `php://filter/...` URI directly.

For comparison, the direct resource:

```smarty
{include file="php://filter/read=convert.base64-encode/resource=/tmp/secret.tpl"}
```

is blocked with `stream 'php' not allowed by security setting`.

Affected package:

- Ecosystem: Packagist / Composer
- Package: `smarty/smarty`
- Confirmed affected version: `5.8.0`
- Confirmed source reference from Composer lock: `78d259d3b971c59a0cd719c270cc5cbb740c36a7`
- Current stable version on Packagist at review time: `v5.8.0`
- Packagist usage at review time: 41,113,855 total downloads and 840,604 monthly downloads

Relevant code paths:

- `Smarty\Resource\BasePlugin::load(...)`
- `Smarty\Resource\StreamPlugin::getContent(...)`
- `Smarty\Security::isTrustedStream(...)`

`BasePlugin::load()` maps the built-in resource name `stream` directly to `StreamPlugin` before the code path that checks PHP stream wrappers with `stream_get_wrappers()` and `Security::isTrustedStream($type)`. `StreamPlugin::getContent()` later calls `fopen($filepath, 'r+')` on the nested URI when the resource name contains `://`.

Preconditions:

An application must render templates that are not fully trusted while relying on Smarty Security to restrict local files and PHP stream wrappers. The PoC sets:

```php
$smarty->enableSecurity();
$smarty->security_policy->streams = null;
```

Local reproduction:

The PoC creates a disposable template directory and a separate outside directory. It enables Smarty Security, disables all streams, and then compares three includes:

1. `../outside/secret.tpl` to confirm the ordinary trusted-directory boundary is enforced.
2. `php://filter/...` to confirm direct PHP streams are blocked by `Security::$streams = null`.
3. `stream:php://filter/...` to show the built-in `stream:` resource bypasses the same restriction and reads the outside file.

Run:

```shell
php -d display_errors=1 poc.php
```

Observed sanitized output:

```text
package=smarty/smarty
installed_version=v5.8.0
template_dir=<tmp>/templates
outside_template=<tmp>/outside/secret.tpl
plain_dotdot_include=BLOCKED:Smarty\Exception:Smarty Security: not trusted file path '<tmp>/outside/secret.tpl'
direct_php_filter_include=BLOCKED:Smarty\Exception:stream 'php' not allowed by security setting
stream_php_filter_include=OK:U01BUlRZX1NUUkVBTV9XUkFQUEVSX1NFQ1VSSVRZX0VTQ0FQRQ==
expected_base64=U01BUlRZX1NUUkVBTV9XUkFQUEVSX1NFQ1VSSVRZX0VTQ0FQRQ==
```

The `plain_dotdot_include` line shows the directory boundary is enforced for ordinary traversal. The `direct_php_filter_include` line shows the same policy rejects `php://filter` when used directly. The `stream_php_filter_include` line shows that wrapping the same URI in Smarty's `stream:` resource bypasses that restriction and reads the outside file.

Impact:

A template author can bypass Smarty Security stream restrictions and read local files that are readable by the PHP process. With `php://filter`, file contents can be base64 encoded and rendered back through the template. This bypasses both the intended `Security::$streams = null` restriction and the normal trusted-template-directory check that blocks `../` traversal.

Duplicate checks:

- OSV query for `Packagist/smarty/smarty` version `5.8.0` returned no vulnerabilities.
- GitHub advisory query for `ecosystem=composer` and `affects=smarty/smarty` returned historical Smarty advisories, including sandbox escapes, PHP code injection, XSS, and older path traversal issues. The listed path traversal advisories affect older versions and do not describe this current `stream:php://filter` resource-wrapper bypass in 5.8.0.
- GitHub issue search in `smarty-php/smarty` for `stream:php://filter` returned zero results.
- Public searches for `Smarty StreamPlugin php://filter` and `smarty/smarty isTrustedStream stream:` did not identify a clear public duplicate during triage.

Suggested remediation:

When resolving the built-in `stream:` resource, parse and validate the nested URI scheme before opening it. For example, `stream:php://filter/...` should call `Security::isTrustedStream('php')`, and `Security::$streams = null` should block the resource before `StreamPlugin::getContent()` reaches `fopen()`.

It would also be safer for `StreamPlugin` to reject nested stream wrappers by default unless the underlying wrapper is explicitly allowed by the active security policy.

## References
- https://github.com/smarty-php/smarty/security/advisories/GHSA-rjhh-76wf-8xmw
- https://github.com/smarty-php/smarty/pull/1195
- https://github.com/smarty-php/smarty/commit/3c9f77a2e06ce319ae0092496af32cc8f3adc52e
- https://github.com/smarty-php/smarty
- https://github.com/smarty-php/smarty/releases/tag/v5.8.4
