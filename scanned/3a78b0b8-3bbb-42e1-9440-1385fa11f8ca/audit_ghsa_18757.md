# [M] Alt Redirect: Potential Authentication Bypass by Spoofing  through query-string stripping logic flaw

## Summary
Severity: Medium
Advisory: GHSA-rpjr-pcmr-9ppw
CVE: CVE-2025-60868
CWE: CWE-290
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-rpjr-pcmr-9ppw
Type: github-advisory

## Affected
- Packagist: `alt-design/alt-redirect` — affected >=0 <1.6.4

## Details
The Alt Redirect 1.6.3 addon for Statamic fails to consistently strip query string parameters when the "Query String Strip" feature is enabled. Case variations, encoded keys, and duplicates are not removed, allowing attackers to bypass sanitization. This may lead to cache poisoning, parameter pollution, or denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60868
- https://github.com/alt-design/Alt-Redirect-Addon/commit/5dc6753c7151ac994c63e18914998991b1f65cbd
- https://gist.github.com/kasiasok/870933de18d1400fa8be88e1bcadec6c
- https://github.com/alt-design/Alt-Redirect-Addon
- https://github.com/alt-design/Alt-Redirect-Addon/releases/tag/v1.6.4
- https://statamic.com/addons/alt-design/alt-redirects/release-notes
