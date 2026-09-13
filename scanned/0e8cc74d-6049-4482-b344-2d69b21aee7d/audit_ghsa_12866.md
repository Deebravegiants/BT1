# [M] XML-RPC for PHP's debugger vulnerable to possible XSS attack

## Summary
Severity: Medium
Advisory: GHSA-pxqj-xrv5-qvjf
CWE: CWE-79
Ecosystem: Packagist
Published: 2023-01-11
Source: https://github.com/advisories/GHSA-pxqj-xrv5-qvjf
Type: github-advisory

## Affected
- Packagist: `phpxmlrpc/phpxmlrpc` — affected >=0 <4.9.2

## Details
The bundled xml-rpc debugger is susceptible to XSS attacks.

Since the debugger is not designed to be exposed to end users but only to the developers using this library, and in the default configuration it is not exposed to requests from the web, the likelihood of exploitation may be low.

## References
- https://github.com/gggeek/phpxmlrpc/security/advisories/GHSA-pxqj-xrv5-qvjf
- https://github.com/gggeek/phpxmlrpc
- https://github.com/gggeek/phpxmlrpc/releases/tag/4.9.2
