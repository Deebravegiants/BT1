# [M] PhpWeasyPrint vulnerable to SSRF and local file disclosure via the attachment option

## Summary
Severity: Medium
Advisory: GHSA-x8g9-h984-pc36
CVE: CVE-2026-49359
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-x8g9-h984-pc36
Type: github-advisory

## Affected
- Packagist: `pontedilana/php-weasyprint` — affected >=0 <2.6.0

## Details
### Summary

`pontedilana/php-weasyprint` fetches the content of option values server-side via `file_get_contents()` when the value looks like a URL, without restricting the URL scheme. The `attachment` option of `Pdf` is the reachable sink: any value that passes `isOptionUrl()` (`filter_var(..., FILTER_VALIDATE_URL)`) is downloaded by the PHP process and embedded into the generated PDF. Because `FILTER_VALIDATE_URL` accepts `http`, `https`, `ftp`, `file` and PHP stream wrappers such as `php://`, an attacker who can influence the `attachment` value reaches both a **Server-Side Request Forgery** primitive (e.g. internal HTTP endpoints, cloud metadata) and a **local file disclosure** primitive (`file://`, `php://filter/...`), with the fetched bytes exfiltrated as a PDF attachment.

This is the same class of issue KnpLabs/snappy patched for its `xsl-style-sheet` option in [GHSA-c5fp-p67m-gq56](https://github.com/KnpLabs/snappy/security/advisories/GHSA-c5fp-p67m-gq56). The library is documented as a one-to-one substitute for KnpLabs/snappy and shares the same code shape.

### Affected versions

`pontedilana/php-weasyprint` versions `<= 2.5.1`.

Patched in: `2.6.0`.

### Privilege required

Any caller that can influence the `attachment` option value handed to `Pdf::generate()` / `Pdf::getOutput()` / `setOption('attachment', ...)`. Typical reach paths: a value sourced from a request parameter, a per-tenant configuration row, or any user-controllable field that flows into the attachment list.

### Vulnerable code

`src/Pdf.php` — `isOptionUrl()` accepts any well-formed URL regardless of scheme:

```php
protected function isOptionUrl($option): bool
{
    return false !== \filter_var($option, \FILTER_VALIDATE_URL);
}
```

`src/Pdf.php` — `handleArrayOptions()` fetches the URL content for the `attachment` option:

```php
$fetchUrlContent = 'attachment' === $option && $this->isOptionUrl($item);
if ($saveToTempFile || $fetchUrlContent) {
    $fileContent = $fetchUrlContent ? \file_get_contents($item) : $item;
    $returnOptions[] = $this->createTemporaryFile($fileContent, $this->optionsWithContentCheck[$option] ?? 'temp');
}
```

`FILTER_VALIDATE_URL` returns truthy for `http://`, `https://`, `ftp://`, `file://localhost/...`, and `php://filter/...`, so `\file_get_contents()` is invoked on attacker-chosen schemes with no allow-list.

### Proof of concept

```php
<?php
use Pontedilana\PhpWeasyPrint\Pdf;

$pdf = new Pdf('/usr/local/bin/weasyprint');

// Attacker-controlled attachment value (e.g. from a request / tenant config):
//   SSRF:               http://169.254.169.254/latest/meta-data/iam/security-credentials/
//   Local file read:    php://filter/convert.base64-encode/resource=/etc/passwd
$attachment = $_GET['doc'];

$pdf->generate('page.html', 'out.pdf', [
    'attachment' => $attachment,
]);

// The bytes fetched server-side by file_get_contents() are embedded in out.pdf,
// allowing the attacker to read internal HTTP responses or local files.
```

### Impact

- **SSRF**: the server fetches arbitrary `http(s)`/`ftp` URLs, reaching internal-only services, link-local metadata endpoints, etc.
- **Local file / wrapper disclosure**: `php://filter/...` (and similar) let an attacker read and exfiltrate local file content inside the generated PDF.
- Affects any consumer that does not fully control the `attachment` option value.

Note: passing a plain local path (e.g. `/etc/passwd`) or a `file://` path that resolves to an existing file is handled as a normal local attachment and is **not** the issue addressed here — that is the documented local-attachment feature (callers must not pass untrusted input to the option). The fix specifically removes the server-side fetch amplification through non-`http(s)` schemes.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (6.5, Medium) — adjust `PR`/`S`/`A` to the consuming application's reachability (e.g. `PR:N` if the attachment value is reachable from an unauthenticated surface).

CWE-918 (Server-Side Request Forgery); secondary CWE-22 (Improper Limitation of a Pathname) for the wrapper-based file read.

### Suggested fix

Restrict the schemes the library will fetch to an allow-list (`http`, `https` by default), and treat any other scheme as inline content instead of fetching it:

```php
private array $allowedSchemes = ['http', 'https'];

// new optional 4th constructor argument: ?array $allowedSchemes = null

protected function isOptionUrl($option): bool
{
    $url = \parse_url((string)$option);

    return false !== $url
        && isset($url['scheme'])
        && \in_array(\strtolower($url['scheme']), $this->allowedSchemes, true);
}
```

A value with a non-allowed scheme (`file://`, `php://`, `ftp://`, ...) is then never passed to `file_get_contents()`.

### Credit

Reported upstream to KnpLabs/snappy ([GHSA-c5fp-p67m-gq56](https://github.com/KnpLabs/snappy/security/advisories/GHSA-c5fp-p67m-gq56)); identified as applicable to `pontedilana/php-weasyprint`, which mirrors the same code.

## References
- https://github.com/KnpLabs/snappy/security/advisories/GHSA-c5fp-p67m-gq56
- https://github.com/pontedilana/php-weasyprint/security/advisories/GHSA-x8g9-h984-pc36
- https://nvd.nist.gov/vuln/detail/CVE-2026-49359
- https://github.com/pontedilana/php-weasyprint/commit/9582dcf119a405276cf55e9e10bc577a887792cb
- https://github.com/pontedilana/php-weasyprint
- https://github.com/pontedilana/php-weasyprint/releases/tag/2.6.0
