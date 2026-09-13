# [M] amphp/http-client Header leakage on cross-domain redirects

## Summary
Severity: Medium
Advisory: GHSA-8jp9-mpv9-98rj
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-8jp9-mpv9-98rj
Type: github-advisory

## Affected
- Packagist: `amphp/http-client` — affected >=4.0.0 <4.4.0

## Details
amphp/http-client has a security weakness that might leak sensitive request headers from the initial request to the redirected host on cross-domain redirects, which were not removed correctly. `Message::setHeaders` does not replace the entire set of headers, but only operates on the headers matching the given array keys.

## References
- https://github.com/amphp/http-client/commit/fa7925363e6d5a0d0d337e2e6eb1affb93cf226e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/amphp/http-client/2020-06-16.yaml
- https://github.com/amphp/http-client
- https://github.com/amphp/http-client/releases/tag/v4.4.0
