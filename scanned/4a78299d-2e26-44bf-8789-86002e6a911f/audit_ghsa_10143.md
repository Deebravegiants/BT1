# [H] elFinder: Command injection in resize background color parameter when using ImageMagick CLI

## Summary
Severity: High
Advisory: GHSA-8q4h-8crm-5cvc
CVE: CVE-2026-41247
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-8q4h-8crm-5cvc
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.67

## Details
### Severity
**High**  
`bg` can be injected into shell command construction, leading to possible RCE in affected configurations.

### Summary

elFinder contains a command injection vulnerability in the `resize` command.

The `bg` (background color) parameter is accepted from user input and passed through image resize/rotate processing. In configurations that use the ImageMagick CLI backend, this value is incorporated into shell command strings without sufficient escaping. An attacker able to invoke the `resize` command with a crafted `bg` value may achieve arbitrary command execution as the web server process user.

This issue affects configurations where:
- the `resize` command is enabled,
- image processing uses the ImageMagick CLI backend, and
- the vulnerable code paths are reachable.


### Impact

An attacker may execute arbitrary OS commands with the privileges of the web server process.

Impact depends on server configuration, enabled commands, backend image library selection, and surrounding deployment controls.


### Affected versions

Affected: all versions before 2.1.66
Patched: 2.1.67


### Details

The vulnerable flow is:

1. The `resize` command accepts the `bg` parameter from the request.
2. The parameter is passed into volume resize handling.
3. In ImageMagick CLI code paths, the value is interpolated into shell command strings.
4. Because the value is not safely constrained and escaped, shell metacharacters may be injected.

The issue was addressed by:
- validating `bg` against a strict allowlist of supported color formats, and
- safely escaping the value before it is passed into CLI command construction.


### Workarounds

Possible mitigations for users who cannot upgrade immediately:

- disable the `resize` command if not required,
- avoid using the ImageMagick CLI backend for image processing,
- restrict access to trusted users only.

Upgrading to the patched release is strongly recommended.


### Credits

Thanks to Lin, WeiChi and Drew Webber for the responsible disclosure.

## References
- https://github.com/Studio-42/elFinder/security/advisories/GHSA-8q4h-8crm-5cvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-41247
- https://github.com/Studio-42/elFinder
