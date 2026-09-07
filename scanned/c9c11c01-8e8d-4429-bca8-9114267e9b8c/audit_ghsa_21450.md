# [H] code injection in phpxmlrpc/phpxmlrpc

## Summary
Severity: High
Advisory: GHSA-3fgr-xjr6-xqm8
CWE: CWE-95
Ecosystem: Packagist
Published: 2022-11-28
Source: https://github.com/advisories/GHSA-3fgr-xjr6-xqm8
Type: github-advisory

## Affected
- Packagist: `phpxmlrpc/phpxmlrpc` — affected >=0 <4.9.0

## Details
code injection in `Wrapper::buildClientWrapperCode` via manipulation of the `$client` argument. It was possible to force the client to access local files or connect to undesired urls instead of the intended target server's url.

## References
- https://github.com/gggeek/phpxmlrpc/issues/80
- https://github.com/gggeek/phpxmlrpc/commit/cf6e605e09d001ce520bfa8e7b168cfa514e663b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpxmlrpc/phpxmlrpc/2022-11-28-2.yaml
- https://github.com/gggeek/phpxmlrpc
- https://github.com/gggeek/phpxmlrpc/releases/tag/4.9.0
