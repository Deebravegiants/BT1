# [M] Kirby: System path exposure from error messages in the REST API

## Summary
Severity: Medium
Advisory: GHSA-rf2p-vh74-7vvh
CVE: CVE-2026-69127
CWE: CWE-497
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-rf2p-vh74-7vvh
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.5
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.5.2

## Details
### TL;DR

This vulnerability affects all Kirby sites that have not disabled the REST API with the `'api' => false` option.

It was possible to trigger a PHP error in the API backend that would expose the full filesystem path of the Kirby installation on the server. This could be used to guess the default `content.salt` or prepare specialized attacks.

----

### Introduction

An information exposure occurs when system data or debugging information leaves the program through an output stream or logging function that makes it accessible to unauthorized parties. Using other weaknesses, an attacker could cause errors to occur; the response to these errors can reveal detailed system information, along with other impacts. An attacker can use messages that reveal technologies, operating systems, and product versions to tune the attack against known vulnerabilities in these technologies. A product may use diagnostic methods that provide significant implementation details such as stack traces as part of its error handling mechanism.

### Affected components

Kirby's REST API at `/api` returns JSON data for each request. If an error occurs during processing of the request, a special error handler converts this error to JSON data that API frontends can handle.

The returned data for errors depends on the debugging mode. If the `debug` option is enabled, the JSON data contains fields for the path and line of the affected file, the internal exception class and the API route that caused the error. This data is omitted from error responses in production (when the `debug` option is disabled).

### Impact

Some internal errors may contain sensitive information in the error message itself. This is often the case with PHP errors.

In affected releases, the REST API error handler did not sanitize error messages for sensitive information.

This exposed system information like the full source path to external API users, including users without authentication. This could be used to guess the default `content.salt` or prepare specialized attacks.

### Patches

The problem has been patched in [Kirby 4.9.5](https://github.com/getkirby/kirby/releases/tag/4.9.5) and [Kirby 5.5.2](https://github.com/getkirby/kirby/releases/tag/5.5.2). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, Kirby has hardened the API error handler to only expose full error messages for exceptions in the `Kirby\Exception` namespace. All other errors are only exposed in debug mode (with disguised paths, keeping only the paths relative to the Kirby installation). Outside of debug mode, general exceptions and PHP errors are replaced with a generic error message.

### Credits

Thanks to Peter Levashov (@petersevera) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-rf2p-vh74-7vvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-69127
- https://github.com/getkirby/kirby/commit/469c5a1a2973811591d996bc967eead3565df1f0
- https://github.com/getkirby/kirby/commit/58f819988436b31969078bc4655452dd48546451
- https://github.com/getkirby/kirby
