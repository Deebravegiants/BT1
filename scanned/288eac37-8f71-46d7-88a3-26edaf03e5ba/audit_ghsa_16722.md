# [M] phpxmlrpc/extra XSS in class documenting_xmlrpc_server

## Summary
Severity: Medium
Advisory: GHSA-ww6p-q26w-fr6m
CWE: CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-ww6p-q26w-fr6m
Type: github-advisory

## Affected
- Packagist: `phpxmlrpc/extras` — affected >=0 <0.6.1

## Details
Versions preceding 0.6.1 of the phpxmlrpc/extras project are susceptible to a Cross-Site Scripting (XSS) vulnerability. This vulnerability exists within the class documenting_xmlrpc_server when processing the GET methodName parameter.

## References
- https://github.com/gggeek/phpxmlrpc-extras/commit/65c336e3def9ce71b3e799104d3a6ad15668ddb0
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpxmlrpc/extras/2017-10-29.yaml
- https://github.com/gggeek/phpxmlrpc-extras
- https://github.com/gggeek/phpxmlrpc-extras/releases/tag/0.6.1
