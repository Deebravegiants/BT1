# [H] Snappy: Binary path is never shell-escaped due to an inverted is_executable check

## Summary
Severity: High
Advisory: GHSA-vpr4-p6fq-85jc
CVE: CVE-2026-46643
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-vpr4-p6fq-85jc
Type: github-advisory

## Affected
- Packagist: `KnpLabs/knp-snappy` — affected >=0 <1.7.1

## Details
### Impact

On POSIX, escapeshellarg(‘/usr/bin/wkhtmltopdf’) returns the literal string ‘/usr/bin/wkhtmltopdf’ with the single-quote characters included. is_executable() then looks for a file whose actual name contains those quote characters, which essentially never exists. The safe branch is dead code and $command always falls through to the raw, unescaped value.

The rest of the arguments (options, input, output) are escaped correctly, so injection has to land in the binary string itself. That happens whenever the binary path is sourced from configuration that is user-influenced, derived from environment variables that ultimately come from request data, or concatenated with any user-controlled fragment.

#### Proof of concept:

```php
 $pdf = new Knp\Snappy\Pdf(‘wkhtmltopdf; touch /tmp/snappy_rce’);
 $pdf->generate(‘https://example.com’, ‘/tmp/out.pdf’);
 // /tmp/snappy_rce is created.
```

**Impact:** command execution as the PHP process when the binary path is attacker-influenced. Even in deployments where the binary is hard-coded, this is a defensive-in-depth regression: downstream packages reasonably assume Snappy shell-escapes the binary because the code looks like it does.

### Patches

The version 1.7.1 will resolve this security advisory.

### Workarounds

Before calling the constructor, ensure `\is_executable($path)` is truthy.

```php
// Bad example
$pdf = new Knp\Snappy\Pdf('/path/to/binary');
```

```php
// Better example
$pathToBinary = '/path/to/binary';

if (!\is_executable($pathToBinary)) {
  throw new \RuntimeException();
}

$pdf = new Knp\Snappy\Pdf('/path/to/binary');
```

## References
- https://github.com/KnpLabs/snappy/security/advisories/GHSA-vpr4-p6fq-85jc
- https://nvd.nist.gov/vuln/detail/CVE-2026-46643
- https://github.com/KnpLabs/snappy
- https://github.com/KnpLabs/snappy/releases/tag/v1.7.1
