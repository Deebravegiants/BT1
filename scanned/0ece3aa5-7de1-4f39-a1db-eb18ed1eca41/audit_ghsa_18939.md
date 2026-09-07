# [M] REDAXO CMS is vulnerable to Reflected XSS in Mediapool Info Banner via args[types]

## Summary
Severity: Medium
Advisory: GHSA-x6vr-q3vf-vqgq
CVE: CVE-2025-66026
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-x6vr-q3vf-vqgq
Type: github-advisory

## Affected
- Packagist: `redaxo/source` — affected >=0 <5.20.1

## Details
### Summary
A reflected Cross-Site Scripting (XSS) vulnerability exists in the Mediapool view where the request parameter `args[types]` is rendered into an info banner without HTML-escaping. This allows arbitrary JavaScript execution in the backend context when an authenticated user visits a crafted link while logged in.

### Details

Control Flow:

1. `redaxo/src/addons/mediapool/pages/index.php` reads args via `rex_request('args', 'array')` and passes them through as `$argUrl` to `media.list.php`.
2. `redaxo/src/addons/mediapool/pages/media.list.php` injects `$argUrl['args']['types']` into an HTML string without escaping:

```
if (!empty($argUrl['args']['types'])) {
    echo rex_view::info(rex_i18n::msg('pool_file_filter') . ' <code>' . $argUrl['args']['types'] . '</code>');
}
```

### PoC

1. Log into the REDAXO backend.
2. While authenticated, open a crafted URL like: `<host>/index.php?page=mediapool/media&args[types]="><img+src%3Dx+onerror%3Dalert%28document.domain%29>`
4. The info banner displays the unescaped value and activates the injected onerror handler, which opens an alert pop-up.

### Impact
Arbitrary JavaScript execution in the backend, enabling theft of session cookies, CSRF tokens, or other sensitive data, and allowing an attacker to perform any administrative actions on behalf of the affected user.

## References
- https://github.com/redaxo/redaxo/security/advisories/GHSA-x6vr-q3vf-vqgq
- https://nvd.nist.gov/vuln/detail/CVE-2025-66026
- https://github.com/redaxo/redaxo/commit/58929062312cf03e344ab04067a365e6b6ee66aa
- https://github.com/redaxo/redaxo
