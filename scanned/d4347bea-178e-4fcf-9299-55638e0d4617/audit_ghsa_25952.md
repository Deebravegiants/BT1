# [H] Arbitrary shell execution

## Summary
Severity: High
Advisory: GHSA-3988-h75v-hwf6
Ecosystem: Packagist
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-3988-h75v-hwf6
Type: github-advisory

## Affected
- Packagist: `squizlabs/php_codesniffer` — affected >=3.0.0 <3.0.1

## Details
A properly crafted filename would allow for arbitrary code execution when using the --filter=gitmodified command line option

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/squizlabs/php_codesniffer/2017-05-18.yaml
- https://github.com/squizlabs/PHP_CodeSniffer
- https://github.com/squizlabs/PHP_CodeSniffer/releases/tag/3.0.1
