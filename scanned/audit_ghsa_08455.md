# [M] Setup PHP: Command Injection in Repository-Derived PHP Version Resolution

## Summary
Severity: Medium
Advisory: GHSA-pqwm-q9pv-ph8r
CVE: CVE-2026-46420
CWE: CWE-78
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-pqwm-q9pv-ph8r
Type: github-advisory

## Affected
- GitHub Actions: `shivammathur/setup-php` — affected >=2.25.0 <2.37.1

## Details
### Summary

A command injection vulnerability was identified in `shivammathur/setup-php` when the action resolves the PHP version from repository-controlled files and uses that value while generating the platform setup script.

In affected versions, `setup-php` may read the PHP version from:

- `.php-version`
- `composer.lock` via `platform-overrides.php`
- `composer.json` via `config.platform.php`

If an attacker can influence one of these files and the workflow executes `setup-php` in a trusted context, they may be able to execute commands on the GitHub Actions runner.

### Impact

This issue is exploitable when `setup-php` is run after checking out attacker-controlled repository contents and resolves the PHP version from repository files.

The most significant example is a privileged workflow such as `pull_request_target` that checks out untrusted pull request code before invoking `setup-php`. Similar risk can also arise in other workflows that operate on attacker-controlled refs, branches, or repository contents in a trusted context.

This is not a separate security boundary when an attacker can already modify the workflow definition itself or directly control the `php-version` workflow input, since that level of access already permits arbitrary command execution in GitHub Actions.

### Technical details

In affected versions, repository-derived PHP version values were insufficiently constrained before being incorporated into the generated shell or PowerShell setup script executed by the action. This could allow attacker-controlled values from supported repository files to influence script execution in trusted workflow contexts.

### Remediation

If you are using `shivammathur/setup-php@v2`, no action is needed on your end. Users who pin the setup-php release version or release version SHA should upgrade to a patched version.

The fix validates PHP version inputs, constrains manifest-derived versions, hardens script generation at the execution, and includes additional checks in related input-handling paths.

## References
- https://github.com/shivammathur/setup-php/security/advisories/GHSA-pqwm-q9pv-ph8r
- https://github.com/shivammathur/setup-php/commit/eeef37e059fb5368a5bc8ed8ce45ff54bd39b80b
- https://github.com/shivammathur/setup-php
