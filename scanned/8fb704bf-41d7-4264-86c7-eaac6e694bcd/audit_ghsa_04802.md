# [M] symfony/ux-live-component: XSS via attacker-controlled child component tag

## Summary
Severity: Medium
Advisory: GHSA-38x5-rcv4-xf7x
CVE: CVE-2026-49210
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-38x5-rcv4-xf7x
Type: github-advisory

## Affected
- Packagist: `symfony/ux-live-component` — affected >=2.8.0 <2.36.0
- Packagist: `symfony/ux-live-component` — affected >=3.0.0 <3.1.0

## Details
### Description

`Symfony\UX\LiveComponent\Util\ChildComponentPartialRenderer::createHtml()` interpolates the `$childTag` argument directly into the HTML output as a tag name, without escaping or validation. The value originates from client-controlled JSON (`children[id].tag`) parsed by `LiveComponentSubscriber` and propagated through `InterceptChildComponentRenderSubscriber`, so an attacker who can reach the Live Component endpoint can inject arbitrary HTML, including `<script>` tags, on any re-render of a Live Component that contains at least one child component.

In the default configuration, the Live Component endpoint is gated by an `Accept: application/vnd.live-component+html` request-header check that cannot be set cross-origin without a CORS preflight, so the issue is primarily a defense-in-depth gap. It becomes directly exploitable on applications that have relaxed CORS to allow this header from untrusted origins, or that have been pivoted from another same-origin XSS.

### Resolution

`ChildComponentPartialRenderer` now validates `$childTag` against a strict HTML tag-name regex before interpolating it, and rejects any value that doesn't match. Anything that wouldn't be a valid HTML tag is dropped before reaching the response.

The patch for this issue is available [here](https://github.com/symfony/ux/commit/fbc5e9a1bda7e4556be21bb1d970f382760ed9a9) for branch 2.x (and forward-ported to 3.x).

### Credits

Symfony would like to thank Pascal Cescon for reporting the issue and Hugo Alliaume for providing the fix.

## References
- https://github.com/symfony/ux/security/advisories/GHSA-38x5-rcv4-xf7x
- https://github.com/symfony/ux/commit/fbc5e9a1bda7e4556be21bb1d970f382760ed9a9
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/ux-live-component/CVE-2026-49210.yaml
- https://github.com/symfony/ux
