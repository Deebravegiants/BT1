# [M] Loofah: SVG `href` attribute bypasses local-reference restriction

## Summary
Severity: Medium
Advisory: GHSA-9wjq-cp2p-hrgf
CVE: CVE-2026-73490
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-9wjq-cp2p-hrgf
Type: github-advisory

## Affected
- RubyGems: `loofah` — affected >=0 <2.25.2

## Details
## Summary

Loofah's HTML5 sanitizer restricted only the `xlink:href` attribute on certain SVG elements to local, same-document references. Browsers also accept a plain `href` attribute as an alternative to the deprecated `xlink:href` per the SVG 2 spec, but Loofah did not apply the same restriction to it, allowing those elements to reference arbitrary external documents.

## Impact

SVG `<use>` can load and render external SVG content by reference. If the referenced external SVG is same-origin and contains scripts or other dangerous content, it could execute in the context of the sanitized document. `<feImage>` can load external images, which can be used for tracking. Modern browsers restrict cross-origin `<use>` fetches, which limits but does not eliminate the risk.

Applications that sanitize user-supplied SVG (directly, or as part of HTML) with Loofah's default allowlist are affected.

## Mitigation

Upgrade to Loofah >= 2.25.2.

## Credit

Found by the maintainer, Mike Dalessio, during a security audit.

## References
- https://github.com/flavorjones/loofah/security/advisories/GHSA-9wjq-cp2p-hrgf
- https://github.com/flavorjones/loofah/commit/20867b9be689521887364b74822c41ef830523c9
- https://github.com/flavorjones/loofah
- https://github.com/flavorjones/loofah/releases/tag/v2.25.2
