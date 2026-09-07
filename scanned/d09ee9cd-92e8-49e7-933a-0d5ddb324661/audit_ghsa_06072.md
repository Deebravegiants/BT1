# [M] Craft CMS: Authenticated leak of secret environment variables

## Summary
Severity: Medium
Advisory: GHSA-596p-6jv8-775v
CVE: CVE-2026-72782
CWE: CWE-668
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-596p-6jv8-775v
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.6
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.18.2

## Details
Environment variables and secrets are interpolated into a Twig template even when the Twig sandbox is enabled, allowing them to be leaked by an authenticated attacker.

The Craft vulnerability [CVE-2026-31857](https://github.com/craftcms/cms/security/advisories/GHSA-fp5j-j7j4-mcxc) was only patched by applying sandboxed Twig templating. This theoretically protects Craft CMS against RCE attacks, provided the sandbox is enabled and secure, with no known bypasses.

However, the same request parameter `elementId,` which allows for sandboxed Twig templates to be rendered, also includes functionality that interpolates referenced environment variables. If the parameter includes a string of the form `${ENV_VAR}` then the string is replaced with the environment variable or secret from a secrets file with that name.

Afterward, the string is rendered as a Twig template. If the sandbox is disabled, Twig templates can already gain RCE or access environment variables using the getenv function. Sandboxed Twig templates should not have this access, but now do thanks to this additional environment-variable replacement behavior.

The template’s resulting value is not directly reflected in the response. To exfiltrate the value, the sandboxed Twig template cannot use network functions. But it can use a blind error-based approach similar to blind SQL injection. With enough requests, any environment variable or secret can be incrementally leaked. This can be abused to forge a session, escalate privileges with the `CRAFT_SECURITY_KEY`, and steal credentials for the database, SMTP server, or other connected APIs or blob storage.

## Impact

An authenticated attacker, with permission to access the control panel, can render a malicious Twig template and steal arbitrary environment variables and secrets with a large number of requests, even if the Twig sandbox is enabled through `enableTwigSandbox()`.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-596p-6jv8-775v
- https://nvd.nist.gov/vuln/detail/CVE-2026-72782
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.18.2
- https://github.com/craftcms/cms/releases/tag/5.10.6
- https://www.vulncheck.com/advisories/craft-cms-rc1-before-environment-variable-leak
