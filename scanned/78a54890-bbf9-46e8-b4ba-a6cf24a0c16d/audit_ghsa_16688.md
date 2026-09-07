# [M] Twig Path Traversal vulnerability in the filesystem loader

## Summary
Severity: Medium
Advisory: GHSA-7cvr-xhm5-x998
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-7cvr-xhm5-x998
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=1.0.0 <1.12.3

## Details
Twig is affected by path traversal vulnerability when used with Twig_Loader_Filesystem for loading Twig templates but only if the application is using non-trusted template names (names provided by a end-user for instance).

When affected, it is possible to go up one directory for the paths configured in the application's loader.

For instance, if the filesystem loader is configured with /path/to/templates as a path to look for templates, an attacker can force Twig to include a file stored in /path/to by prepending the path with /../ like in {% include "/../somefile_in_path_to" %}

Note that using anything else (like ../somefile, /../../somefile, or ../../somefile) won’t work and the application will return a proper exception.

## References
- https://github.com/fabpot/Twig/commit/3d19a2eed53570776af313593aaeb5ad62cf4980.diff
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/2013-04-08.yaml
- https://github.com/twigphp/Twig
- https://web.archive.org/web/20130511111630/http://blog.twig.sensiolabs.org/post/47461911874/security-release-twig-1-12-3-released
