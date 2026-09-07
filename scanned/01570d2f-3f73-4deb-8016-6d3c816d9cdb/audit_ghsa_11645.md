# [H] Statamic vulnerable to remote code execution via Antlers-enabled control panel inputs

## Summary
Severity: High
Advisory: GHSA-cpv7-q2wx-m8rw
CVE: CVE-2026-28425
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-01
Source: https://github.com/advisories/GHSA-cpv7-q2wx-m8rw
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.16
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.7.2

## Details
### Impact
An authenticated control panel user with access to Antlers-enabled inputs may be able to achieve remote code execution in the application context. That can lead to full compromise of the application, including access to sensitive configuration, modification or exfiltration of data, and potential impact on availability.

Exploitation is only possible where Antlers runs on user-controlled content—for example, content fields with Antlers explicitly enabled (requiring permission to configure fields and to edit entries), built-in config that supports Antlers such as Forms email notification settings (requiring configuration permission), or third-party addons that add Antlers-enabled fields to entries (for example, the SEO Pro addon). In each case the attacker must have the relevant control panel permissions.

### Patches
This has been fixed in 5.73.16 and 6.7.2.

Note that a follow-up report showed that the original 5.73.11 & 6.4.0 fixes were insufficient.

If you use addons that depend on Statamic, ensure that after updating you are running a patched Statamic version.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-cpv7-q2wx-m8rw
- https://nvd.nist.gov/vuln/detail/CVE-2026-28425
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.73.16
- https://github.com/statamic/cms/releases/tag/v6.7.2
