# [H] PHPUnit: Argument injection via newline in PHP INI values forwarded to child processes

## Summary
Severity: High
Advisory: GHSA-mh6w-vxff-9wqp
CWE: CWE-88, CWE-93
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-mh6w-vxff-9wqp
Type: github-advisory

## Affected
- Packagist: `phpunit/phpunit` — affected >=12.5.21 <12.5.22
- Packagist: `phpunit/phpunit` — affected >=13.1.5 <13.1.6

## Details
# Impact

PHPUnit forwards PHP INI settings to child processes (used for isolated/PHPT test execution) as `-d name=value` command-line arguments without neutralizing INI metacharacters. Because PHP's INI parser interprets `"` as a string delimiter, `;` as the start of a comment, and most importantly a newline as a directive separator, a value containing a newline is parsed by the child process as **multiple INI directives**.

An attacker able to influence a single INI value can therefore inject arbitrary additional directives into the child's configuration, including `auto_prepend_file`, `extension`, `disable_functions`, `open_basedir`, and others. Setting `auto_prepend_file` to an attacker-controlled path yields **remote code execution** in the child process.

**Sources of INI values that participate in the attack:**

- `<ini name="…" value="…"/>` entries in `phpunit.xml` / `phpunit.xml.dist`
- INI settings inherited from the host PHP runtime via `ini_get_all()`

## Threat Model

Exploitation requires the attacker to control the content of an INI value read by PHPUnit. In practice this means write access to the project's `phpunit.xml`, the host `php.ini`, or the PHP binary's environment. The most realistic exposure is **Poisoned Pipeline Execution (PPE)**: a pull request from an untrusted contributor that modifies `phpunit.xml` to include a newline-containing INI value, executed by a CI system that runs PHPUnit against the PR without isolation. A malicious newline is not visibly distinguishable from a legitimate value in a typical diff review.

## Affected Component

`PHPUnit\Util\PHP\JobRunner::settingsToParameters()`

## Patches

The fix has two parts:

### 1. Reject line-break characters

Because a newline or carriage return in an INI value has no legitimate use and is the primitive that enables directive injection, any PHP setting value containing `\n` or `\r` is now rejected with an explicit `PhpProcessException`. This follows the same "visibility over silence" principle applied in **CVE-2026-24765**: the anomalous state fails loudly in CI output rather than being silently sanitized, giving operators an opportunity to investigate whether it reflects tampering, environment contamination, or an unexpected upstream change.

### 2. Quote remaining metacharacters

Values containing `"` or `;`, both of which have legitimate uses (e.g., regex-valued INI settings such as ddtrace's `datadog.appsec.obfuscation_parameter_value_regexp`), are wrapped in double quotes with inner `"` escaped as `\"`, so PHP's INI parser reads them as literal string contents rather than comment/delimiter tokens. Plain values are forwarded unchanged so that boolean keywords (`On`/`Off`) and bitwise expressions (`E_ALL & ~E_NOTICE`) retain their INI semantics.

## Workarounds

If upgrading is not immediately possible:

1. **Audit INI values:** Ensure no `<ini value="…">` entry in `phpunit.xml` / `phpunit.xml.dist` contains newline, `"`, or `;` characters, and that nothing writes such values into configuration at build time.
2. **Isolate CI execution of untrusted code:** Run PHPUnit against pull requests only in ephemeral, containerized runners that discard filesystem state between jobs; require human review before executing PRs from forks; enforce branch protection on workflows that handle secrets (`pull_request_target` and similar). These mitigations apply to the broader PPE risk class and are effective against this vulnerability as well.
3. **Restrict who can modify `phpunit.xml`:** Treat `phpunit.xml` as security-sensitive in code review, particularly `<ini>` entries.
4. **Sanitize host INI:** Ensure the host PHP's `php.ini` does not contain values with embedded newlines or unescaped metacharacters.

## References
- https://github.com/sebastianbergmann/phpunit/security/advisories/GHSA-qrr6-mg7r-m243
- https://github.com/sebastianbergmann/phpunit/pull/6592
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpunit/phpunit/GHSA-qrr6-mg7r-m243.yaml
- https://github.com/sebastianbergmann/phpunit
- https://owasp.org/www-project-top-10-ci-cd-security-risks/CICD-SEC-04-Poisoned-Pipeline-Execution
