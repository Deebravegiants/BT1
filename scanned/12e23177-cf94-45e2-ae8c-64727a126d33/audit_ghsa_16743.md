# [H] pygmentize Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-77mv-mp2j-gxxh
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-77mv-mp2j-gxxh
Type: github-advisory

## Affected
- Packagist: `3f/pygmentize` — affected >=0 <1.2

## Details
pygmentize is prone to remote code execution due to an unsafe sanitazation of user input when passed to the `highlight` function.

## References
- https://github.com/dedalozzo/pygmentize/issues/1
- https://github.com/dedalozzo/pygmentize/pull/3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/3f/pygmentize/2017-05-15.yaml
- https://github.com/dedalozzo/pygmentize
