# [H] elFinder unsafe upload filtering leading to remote code execution

## Summary
Severity: High
Advisory: GHSA-qm58-cvvm-c5qr
CVE: CVE-2021-23394
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-15
Source: https://github.com/advisories/GHSA-qm58-cvvm-c5qr
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.58

## Details
### Impact

Before elFinder 2.1.58, the upload filter did not disallow the upload of `.phar` files. As several Linux distributions are now shipping Apache configured in a way it will process these files as PHP scripts, attackers could gain arbitrary code execution on the server hosting the PHP connector (even in minimal configuration).

### Patches

The issue has been addressed with https://github.com/Studio-42/elFinder/commit/75ea92decc16a5daf7f618f85dc621d1b534b5e1, associating `.phar` files to the right MIME type. Unless explicitly allowed in the configuration, such files cannot be uploaded anymore. This patch is part of the last release of elFinder, 2.1.58.

### Workarounds

If you can't update to 2.1.58, make sure your connector is not exposed without authentication.

### Important tips

Server-side scripts can often be created as text files. Currently, elFinder has an appropriate MIME type set for file extensions that are generally runnable on a web server.

However, the server has various settings. In some cases, the executable file may be judged as "text/plain". Therefore, elFinder installers should understand the extensions that can be executed on the web server where elFinder is installed, and check if there are any missing items in the elFinder settings.

The elFinder PHP connector has an option "additionalMimeMap" that specifies the MIME type for each extension. See [#3295(comment)](https://github.com/Studio-42/elFinder/issues/3295#issuecomment-853042139) for more information.

### References

- https://snyk.io/vuln/composer:studio-42%2Felfinder
- https://github.com/Studio-42/elFinder/issues/3295
- Further technical details will be disclosed on https://blog.sonarsource.com/tag/security after some time.

### For more information

If you have any questions or comments about this advisory, you can contact:
- The original reporters, by sending an email to  support [at] snyk.io or vulnerability.research [at] sonarsource.com;
- The maintainers, by opening an issue on this repository.

## References
- https://github.com/Studio-42/elFinder/security/advisories/GHSA-qm58-cvvm-c5qr
- https://nvd.nist.gov/vuln/detail/CVE-2021-23394
- https://github.com/Studio-42/elFinder/issues/3295
- https://github.com/Studio-42/elFinder/commit/75ea92decc16a5daf7f618f85dc621d1b534b5e1
- https://blog.sonarsource.com/elfinder-case-study-of-web-file-manager-vulnerabilities
- https://github.com/Studio-42/elFinder
- https://snyk.io/vuln/SNYK-PHP-STUDIO42ELFINDER-1290554
