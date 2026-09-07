# [M] Symfony has Email Header Injection via Non-Token Characters in Mime Parameter Names

## Summary
Severity: Medium
Advisory: GHSA-vqc8-7275-q272
CVE: CVE-2026-45070
CWE: CWE-93
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-vqc8-7275-q272
Type: github-advisory

## Affected
- Packagist: `symfony/mime` — affected >=0 <5.4.52
- Packagist: `symfony/symfony` — affected >=0 <5.4.52
- Packagist: `symfony/mime` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/mime` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/mime` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

`Symfony\Component\Mime\Header\ParameterizedHeader` (and the related parameter handling reachable from `Symfony\Component\Mime\Header\Headers`) is responsible for serializing structured headers such as `Content-Type` and `Content-Disposition`, which carry `key=value` parameters (e.g. `Content-Disposition: attachment; filename="x"`).

RFC 2045 / RFC 5322 require parameter *names* to be `tokens`: a restricted ASCII subset that excludes whitespace, CR/LF, and the `tspecials` set. Symfony's parameter handling validates and properly encodes parameter *values*, but does not validate parameter *names*: the supplied name is emitted verbatim into the serialized header.

A caller that derives a parameter name from untrusted input, e.g. an application that lets a user influence a `Content-Disposition` parameter name, can include `\r\n` or other non-token bytes inside the name, terminating the current header and injecting additional headers in the rendered message. This is the classic CRLF / header-injection primitive applied to the parameter-name slot.

### Resolution

`ParameterizedHeader` now rejects parameter names that contain bytes outside the RFC `token` character class.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/e62ea217f8b4ca8ae922ad0f949e0c4dc1f9b613) for branch 5.4.

### Credits

Symfony would like to thank Fabian Fleischer for reporting the issue and Alexandre Daubois for fixing it.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-vqc8-7275-q272
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/mime/CVE-2026-45070.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45070.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45070
