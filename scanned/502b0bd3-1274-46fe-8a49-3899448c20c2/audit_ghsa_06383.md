# [M] Smarty: SSRF via redirect bypass of trusted_uri using {fetch}

## Summary
Severity: Medium
Advisory: GHSA-cq55-c7wv-pxmq
CVE: CVE-2026-62993
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-cq55-c7wv-pxmq
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=5.0.0 <5.8.2
- Packagist: `smarty/smarty` — affected >=0 <4.5.7

## Details
When a Security policy is active, {fetch} validates the requested remote URL against the trusted_uri allowlist via Security::isTrustedUri(). For non-http:// schemes (e.g. https://) the resource was then read with file_get_contents(), which follows HTTP redirects by default. Because isTrustedUri() only validates the initial URL, an open redirect on an otherwise-trusted host could be used to redirect the request to a non-trusted, internal target — bypassing the trusted_uri policy.

## Impact

An attacker who can supply a fetch target (or influence one) and who has an open redirect available on a trusted host can cause the server to issue requests to attacker-chosen internal endpoints, defeating the trusted_uri allowlist (server-side request forgery).

## Patches

Fixed in 5.8.2. When a security policy is active, {fetch} now passes a stream context that disables redirect following (follow_location => 0, max_redirects => 1) to file_get_contents() for remote resources. Behavior is unchanged when no security policy is set, since there is no trusted_uri to bypass.

## Workarounds

Avoid fetching remote resources from within templates under untrusted control; ensure hosts listed in trusted_uri do not expose open redirects.

## References
- https://github.com/smarty-php/smarty/security/advisories/GHSA-cq55-c7wv-pxmq
- https://nvd.nist.gov/vuln/detail/CVE-2026-62993
- https://github.com/smarty-php/smarty/pull/1194
- https://github.com/smarty-php/smarty/commit/31e06fc087a8b5a9b236c1e5dacc1c2850a2c115
- https://github.com/smarty-php/smarty/commit/a1ccdb0518021a559b4066c37b76a42c86bbce90
- https://github.com/smarty-php/smarty
- https://github.com/smarty-php/smarty/releases/tag/v4.5.7
- https://github.com/smarty-php/smarty/releases/tag/v5.8.2
