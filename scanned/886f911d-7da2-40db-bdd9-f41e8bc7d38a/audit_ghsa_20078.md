# [M] phpxmlrpc vulnerable to argument injection

## Summary
Severity: Medium
Advisory: GHSA-q7qq-9gx2-ggxv
CWE: CWE-88
Ecosystem: Packagist
Published: 2022-12-02
Source: https://github.com/advisories/GHSA-q7qq-9gx2-ggxv
Type: github-advisory

## Affected
- Packagist: `phpxmlrpc/phpxmlrpc` — affected >=0 <4.9.0

## Details
phpxmlrpc vulnerable to argument injection via  local file access in `Client:send` via manipulation of `$protocol` argument.

## References
- https://github.com/gggeek/phpxmlrpc/issues/81
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpxmlrpc/phpxmlrpc/2022-11-28-1.yaml
- https://github.com/gggeek/phpxmlrpc
- https://github.com/gggeek/phpxmlrpc/releases/tag/4.9.0
