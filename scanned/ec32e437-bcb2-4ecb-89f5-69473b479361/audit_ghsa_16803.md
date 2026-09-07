# [M] symbiote/silverstripe-multivaluefield Possible PHP Object Injection via Multi-Value Field Extension

## Summary
Severity: Medium
Advisory: GHSA-g5vj-wj9x-4jg9
CWE: CWE-74, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-29
Source: https://github.com/advisories/GHSA-g5vj-wj9x-4jg9
Type: github-advisory

## Affected
- Packagist: `symbiote/silverstripe-multivaluefield` — affected >=3.0.0 <3.1.0

## Details
A potential deserialisation vulnerability has been identified in the symbiote/silverstripe-multivaluefield which could allow an attacker to exploit implementations of this module via object injection.

Support for handling PHP objects as values in this module has been deprecated, and the serialisation technique has been switched to using JSON for handling arrays.

As well as this, a potential XSS (cross-site scripting) vulnerability has been identified and remediated.

## References
- https://github.com/symbiote/silverstripe-multivaluefield/commit/31fbc8c208431fc7d7e96da6fa39ca057d978953
- https://github.com/symbiote/silverstripe-multivaluefield/commit/f523dfcb13b2bd9eb110ffa0c83087a49322ad3b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symbiote/silverstripe-multivaluefield/SS-2018-017-1.yaml
- https://github.com/symbiote/silverstripe-multivaluefield
- https://www.silverstripe.org/download/security-releases/ss-2018-017
