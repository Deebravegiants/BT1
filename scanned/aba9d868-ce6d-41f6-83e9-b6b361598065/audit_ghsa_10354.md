# [M] Flarum: Path traversal in LESS parser via theme color settings (incomplete fix for CVE-2023-27577)

## Summary
Severity: Medium
Advisory: GHSA-xjvc-pw2r-6878
CVE: CVE-2026-41887
CWE: CWE-22, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-xjvc-pw2r-6878
Type: github-advisory

## Affected
- Packagist: `flarum/core` — affected >=0 <1.8.16
- Packagist: `flarum/core` — affected >=2.0.0-beta.1 <2.0.0-rc.1

## Details
## Summary

Flarum's patch for [CVE-2023-27577](https://github.com/flarum/framework/security/advisories/GHSA-vhm8-wwrf-3gcw) restricted the `@import` and `data-uri()` LESS features in the `custom_less` setting, but the same restriction was never applied to other settings registered as LESS config variables (for example `theme_primary_color` and `theme_secondary_color`, as well as any key registered via `Extend\Settings::registerLessConfigVar()`).

Those values are interpolated verbatim into the LESS source at compile time, allowing an authenticated administrator to craft a theme-color value that injects an arbitrary `@import` directive into the compiled `forum.css`. Because the underlying LESS parser honours `@import (inline) '<path>'`, an attacker can read arbitrary files reachable by the PHP process (local file inclusion) or trigger outbound HTTP(S) requests (server-side request forgery).

## Impact

An attacker who has compromised — or legitimately obtained — an administrator account can:

- **Read arbitrary local files** reachable by the PHP process (e.g. `/etc/passwd`, `.env`, config files containing database credentials, OAuth secrets, API keys).
- **Trigger outbound HTTP/HTTPS requests** from the Flarum host, enabling SSRF against internal services and cloud metadata endpoints such as `http://169.254.169.254/` (AWS IMDSv1, GCP, Azure).

The contents of the attacker-controlled import are embedded into the compiled `forum.css`, which is publicly served — so the attacker can retrieve whatever was read simply by fetching the CSS file.

This is a privilege-escalation vulnerability: a forum administrator is not intended to have host-level file read or access to internal network resources.

### Example payload

Submitted via `POST /api/settings` with an admin session:

```json
{ "theme_primary_color": "#4D698E;@import (inline) '/etc/passwd';" }
```

The setting is stored verbatim, interpolated into the LESS source on the next CSS compile, and the target file's contents appear in `/assets/forum.css`.

## Patches

- **`flarum/core` 1.8.16** — fix for the 1.x branch.
- **`flarum/core` 2.0.0-rc.1** — fix for the 2.x branch.

The fix extends the existing `@import` / `data-uri()` validation in `Flarum\Forum\ValidateCustomLess::whenSettingsSaving` to every dirty setting whose key is registered as a LESS config variable, not just `custom_less`.

## Workarounds

If upgrading is not immediately possible:

- Ensure administrator accounts are protected with strong, unique passwords and (where supported) two-factor authentication.
- Restrict administrator access to trusted users only.
- Review the forum's public `forum.css` for unexpected content that could indicate prior exploitation.

There is no configuration-level mitigation on affected versions — the fix requires the upgraded code.

## Resources

- [CVE-2023-27577](https://nvd.nist.gov/vuln/detail/CVE-2023-27577) — the original vulnerability whose patch was incomplete.
- [GHSA-vhm8-wwrf-3gcw](https://github.com/flarum/framework/security/advisories/GHSA-vhm8-wwrf-3gcw) — the original advisory.

## Credit

Reported to the Flarum Foundation by **William (Liam) Snow IV** ([@LiamSnow](https://github.com/LiamSnow)), discovered during a graduate-level network security lab at Worcester Polytechnic Institute.

## References
- https://github.com/flarum/framework/security/advisories/GHSA-vhm8-wwrf-3gcw
- https://github.com/flarum/framework/security/advisories/GHSA-xjvc-pw2r-6878
- https://nvd.nist.gov/vuln/detail/CVE-2023-27577
- https://nvd.nist.gov/vuln/detail/CVE-2026-41887
- https://github.com/flarum/framework/commit/2d90a1f19f0e46f8c7e1b07c48ba74b5e38f8410
- https://github.com/flarum/framework
- https://github.com/flarum/framework/releases/tag/v1.8.16
- https://github.com/flarum/framework/releases/tag/v2.0.0-rc.1
