# [M] Zendframework Potential XSS or HTML Injection vector in Zend_Json

## Summary
Severity: Medium
Advisory: GHSA-vvm3-rv48-j3g5
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-vvm3-rv48-j3g5
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.7.0 <1.7.9
- Packagist: `zendframework/zendframework1` — affected >=1.8.0 <1.8.5
- Packagist: `zendframework/zendframework1` — affected >=1.9.0 <1.9.7

## Details
`Zend_Json_Encoder` was not taking into account the solidus character (/) during encoding, leading to incompatibilities with the JSON specification, and opening the potential for XSS or HTML injection attacks when returning HTML within a JSON string.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2010-06.yaml
- https://github.com/zendframework/zf1
- https://web.archive.org/web/20200228150030/https://framework.zend.com/security/advisory/ZF2010-06
