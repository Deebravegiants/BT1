# [H] Path Traversal in total.js

## Summary
Severity: High
Advisory: GHSA-3q32-j57w-q4w7
CVE: CVE-2019-8903
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-02-20
Source: https://github.com/advisories/GHSA-3q32-j57w-q4w7
Type: github-advisory

## Affected
- npm: `total.js` — affected >=0 <3.2.3

## Details
Affected versions of `total.js` are vulnerable to Path Traversal.  Due to insufficient input sanitization in URLs, attackers can access server files outside the `/public` folder by using relative paths.  
The files served are limited to these file types: `flac`, `jpg`, `jpeg`, `png`, `gif`, `ico`, `js`, `css`, `txt`, `xml`, `woff`, `woff2`, `otf`, `ttf`, `eot`, `svg`, `zip`, `rar`, `pdf`, `docx`, `xlsx`, `doc`, `xls`, `html`, `htm`, `appcache`, `manifest`, `map`, `ogv`, `ogg`, `mp4`, `mp3`, `webp`, `webm`, `swf`, `package`, `json`, `md`, `m4v`, `jsx`, `heif`, `heic`.


## Recommendation

- If you are using version 2.1.x, upgrade to 2.1.1 or later.
- If you are using version 2.2.x, upgrade to 2.2.1 or later.
- If you are using version 2.3.x, upgrade to 2.3.1 or later.
- If you are using version 2.4.x, upgrade to 2.4.1 or later.
- If you are using version 2.5.x, upgrade to 2.5.1 or later.
- If you are using version 2.6.x, upgrade to 2.6.3 or later.
- If you are using version 2.7.x, upgrade to 2.7.1 or later.
- If you are using version 2.8.x, upgrade to 2.8.1 or later.
- If you are using version 2.9.x, upgrade to 2.9.5 or later.
- If you are using version 3.0.x, upgrade to 3.0.1 or later.
- If you are using version 3.1.x, upgrade to 3.1.1 or later.
- If you are using version 3.2.x, upgrade to 3.2.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8903
- https://github.com/totaljs/framework/commit/c37cafbf3e379a98db71c1125533d1e8d5b5aef7
- https://github.com/totaljs/framework/commit/de16238d13848149f5d1dae51f54e397a525932b
- https://blog.certimetergroup.com/it/articolo/security/total.js-directory-traversal-cve-2019-8903
- https://github.com/advisories/GHSA-3q32-j57w-q4w7
- https://github.com/totaljs/framework
- https://www.npmjs.com/advisories/1026
