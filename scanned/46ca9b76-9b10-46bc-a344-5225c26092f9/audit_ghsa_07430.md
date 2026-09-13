# [M] Composer: URL-embedded HTTP-Basic username leaks to verbose logs (GitHub PAT exposure)

## Summary
Severity: Medium
Advisory: GHSA-g6xq-892h-64w3
CVE: CVE-2026-59947
CWE: CWE-532
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-g6xq-892h-64w3
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=2.3.0 <2.10.2
- Packagist: `composer/composer` — affected >=1.0.0 <2.2.29

## Details
## Summary

When Composer is run with -vvv (debug verbosity), it could print a credential that was embedded directly in a repository or package URL, but not as a password, to its debug output. Composer already masked the password portion of such URLs, but the username portion was shown in clear text. Because GitHub and several other services support placing an access token in the username position of a URL (for example https://[token]@github.com/owner/repo), a token used that way could end up written to the verbose log in full.

This is an information disclosure issue. The credential is only ever exposed to whoever can already read Composer's debug output.

## Am I affected?

You are potentially affected only if **all** of the following apply:

- A credential is embedded inside a URL that Composer handles, e.g. in a `repositories` entry in composer.json, in a package dist/source URL - rather than being supplied through auth.json or the COMPOSER_AUTH environment variable.
- The secret sits in the username slot of that URL (e.g. `https://TOKEN@host/…`). A normal `username:password@host` pair where the username is an ordinary account name did not expose the password, that was already masked.
- Composer is run with -vvv (debug verbosity), and that output is retained or shared somewhere others can read it: public CI build logs, output pasted into an issue or chat, archived terminal sessions, and so on.

If you keep credentials in auth.json or environment variables, or you never run Composer at debug verbosity, you were not exposed.

The most realistic exposure is the documented pattern of embedding a GitHub Personal Access Token in a URL's username position on a machine (often CI) that captures verbose output.

## Patched versions

The username is now masked the same way the password already was, so an embedded token no longer appears in verbose output (a short, non-secret prefix may be shown to aid debugging, but never the full value).

Fixed in Composer 2.10.2 and the 2.2.29.

## Workarounds

There is no configuration setting that prevents outputting credentials while keeping normal behavior.

If you cannot upgrade right away, you can reduce exposure by:

- Not running Composer with -vvv (debug verbosity) in environments where output is captured or shared.
- Moving credentials out of URLs and into auth.json or COMPOSER_AUTH.
- Scrubbing existing CI/build logs that may already contain a leaked token.

## References
- https://github.com/composer/composer/security/advisories/GHSA-g6xq-892h-64w3
- https://nvd.nist.gov/vuln/detail/CVE-2026-59947
- https://github.com/composer/composer/commit/6bd66874ae523ecb69aca5964487a0cdfda03ef8
- https://github.com/composer/composer/commit/8887ad76fbd830cb1861a2b1fd8ead78ed1fa1ec
- https://github.com/composer/composer
- https://github.com/composer/composer/releases/tag/2.10.2
- https://github.com/composer/composer/releases/tag/2.2.29
