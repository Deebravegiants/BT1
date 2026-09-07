# [M] Lara-zeus Dynamic Dashboard and Artemis do not validate paragraph widget values which can be used for XSS

## Summary
Severity: Medium
Advisory: GHSA-c6cw-g7fc-4gwc
CVE: CVE-2024-47817
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-07
Source: https://github.com/advisories/GHSA-c6cw-g7fc-4gwc
Type: github-advisory

## Affected
- Packagist: `lara-zeus/dynamic-dashboard` — affected >=3.0.0 <3.0.2
- Packagist: `lara-zeus/artemis` — affected >=1.0.0 <1.0.7

## Details
# Summary
If values passed to a paragraph widget are not valid and contain a specific set of characters, applications are vulnerable to XSS attack against a user who opens a page on which a paragraph widget is rendered.

Versions of dynamic dashboard from v3.0.0 through v3.0.2 are affected.

Please upgrade to dynamic dashboard [v3.0.2](https://github.com/lara-zeus/dynamic-dashboard/releases/tag/v3.0.2).

# PoC
>PoC will be published in a few weeks, once developers have had a chance to upgrade their apps.

# Response
This vulnerability (in paragraph widget only) was reported by **Raghav Sharma**, who reported the issue and patched the issue during the morning of 05/10/2024. Thank you **Raghav Sharma**.

The review process concluded the same day at night, which revealed the issue was also present in paragraph widget. This was fixed the same day and dynamic dashboard [v3.0.2](https://github.com/lara-zeus/dynamic-dashboard/releases/tag/v3.0.2) followed.

## Note:
if you're published the view (blade files), you have to republish them or check the changes on release to update the affected file.

## References
- https://github.com/lara-zeus/dynamic-dashboard/security/advisories/GHSA-c6cw-g7fc-4gwc
- https://nvd.nist.gov/vuln/detail/CVE-2024-47817
- https://github.com/lara-zeus/artemis/commit/3a3f9dd8a706af569c5581b20dcfeff91a43b9d9
- https://github.com/lara-zeus/artemis/commit/4636f58628d20d3e78ea8514406bd7da94997f2c
- https://github.com/lara-zeus/dynamic-dashboard/commit/adfb4b1cdfdaa01299631f0e569ce201a7cc545a
- https://github.com/lara-zeus/dynamic-dashboard
