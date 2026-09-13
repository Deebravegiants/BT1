# [M] Snappy : SSRF and local file read via the xsl-style-sheet option

## Summary
Severity: Medium
Advisory: GHSA-c5fp-p67m-gq56
CVE: CVE-2026-46683
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-c5fp-p67m-gq56
Type: github-advisory

## Affected
- Packagist: `knplabs/knp-snappy` — affected >=0 <1.7.0

## Details
### Impact

It impacts applications where:
- the PHP daemon run with root permissions ;
- the application is either running outside a container or has sensitive file access ;

It could happens with this kind of workflows:

```php
$stylesheet = $_GET['stylesheet']; // = ‘file:///etc/passwd’
$pdf = new Knp\Snappy\Pdf(‘/usr/local/bin/wkhtmltopdf’);
 $pdf->generate(‘page.html’, ‘out.pdf’, [
   ‘xsl-style-sheet’ => $stylesheet
 ]);
```

### Patches

A list a schema with `http` and `https` by default is used to validate the remote path by default.

### Workarounds

Developers should ensure usage cannot allow (in any case) a user to pass a free input directly to the Snappy library.

```php
// Bad example
$pdf = new Knp\Snappy\Pdf(‘/usr/local/bin/wkhtmltopdf’);
 $pdf->generate(‘page.html’, ‘out.pdf’, [
   ‘xsl-style-sheet’ => $_GET['input'],
 ]);
```

Instead developers can list available available stylesheets and pick the right one with the user input.

```php
// Better
$allowedStylesheets = [
    'invoice' => '/app/xsl/invoice.xsl',
    'report'  => '/app/xsl/report.xsl',
];

$key = $_GET['stylesheet'] ?? '';

if (!array_key_exists($key, $allowedStylesheets)) {
    throw new \RuntimeException('Unknown stylesheet.');
}

$pdf = new Knp\Snappy\Pdf('/usr/local/bin/wkhtmltopdf');
$pdf->generate('page.html', 'out.pdf', [
    'xsl-style-sheet' => $allowedStylesheets[$key],
]);
```

### References

Read more about SSRF at [owasp.org/www-community/attacks/Server_Side_Request_Forgery](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)

## References
- https://github.com/KnpLabs/snappy/security/advisories/GHSA-c5fp-p67m-gq56
- https://nvd.nist.gov/vuln/detail/CVE-2026-46683
- https://github.com/KnpLabs/snappy
- https://github.com/KnpLabs/snappy/releases/tag/v1.7.0
