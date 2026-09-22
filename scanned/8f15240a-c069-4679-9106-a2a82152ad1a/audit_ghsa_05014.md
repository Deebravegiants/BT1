# [C] PHPSpreadsheet has a patch bypass for CVE-2026-34084 

## Summary
Severity: Critical
Advisory: GHSA-87m4-826x-3crx
CVE: CVE-2026-45034
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-87m4-826x-3crx
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.30.5

## Details
## Summary

CVE-2026-34084 was patched by the helper `File::prohibitWrappers`. The helper calls `parse_url($filename, PHP_URL_SCHEME)` and then checks `is_string($scheme) && strlen($scheme) > 1` to reject stream wrappers such as `phar://`, `php://`, `data://` or `expect://`. The check is not equivalent to "does the path contain a wrapper". When the input has the form `phar:///path/file.phar/inner` with three or more slashes after the scheme, `parse_url` returns boolean `false` instead of returning the scheme string. The `is_string($scheme)` branch is therefore skipped, the helper returns without throwing, and the caller proceeds. PHP's stream layer, however, still treats `phar:///...` as a valid phar wrapper and opens the underlying phar file. The result is that `IOFactory::load($attackerPath)` walks past the patch and still touches the phar wrapper. On PHP 7.x, simply reaching the phar wrapper via `is_file` is enough for PHP to automatically deserialize the phar metadata, which in turn invokes the magic methods `__wakeup` and `__destruct` of an attacker controlled object and gives full RCE. On PHP 8.x, automatic metadata deserialization for plain file ops was removed, so the chain at the PhpSpreadsheet layer reduces to a phar wrapper file read primitive, and RCE only resurfaces if the downstream consumer ever calls `Phar::getMetadata`.

## Vulnerable code

The file `vendor/phpoffice/phpspreadsheet/src/PhpSpreadsheet/Shared/File.php` is byte identical across all six latest tags listed below:

```php
public static function prohibitWrappers(string $filename): void
{
    $scheme = parse_url($filename, PHP_URL_SCHEME);
    if (is_string($scheme) && strlen($scheme) > 1) {
        throw new Exception("Stream wrappers are not permitted as file paths: {$filename}");
    }
}
```

For input `phar://x/dummy.csv` the call returns the string `"phar"` and the throw fires correctly. For input `phar:///work/exploit.phar/dummy.csv` the same call returns `false` and the throw is skipped, which is the bypass.

## Confirmed affected versions

Tested on 2026-05-03. The `prohibitWrappers` source on disk is identical across all six tags.

| Branch | Latest tag | PHP under test | Result |
|---|---|---|---|
| 1.x | 1.30.4 | 7.4 | bypass plus full RCE, gadget wrote marker file |
| 2.1.x | 2.1.16 | 8.3 | bypass |
| 2.4.x | 2.4.5 | 8.3 | bypass |
| 3.10.x | 3.10.5 | 8.3 | bypass |
| 5.6.x | 5.6.0 | 8.3 | bypass |
| 5.7.x | 5.7.0 | 8.3 | bypass |

Version 1.30.4 is the latest tag of the 1.x branch, which is the only branch that still supports PHP 7.x. Version 5.7.0 is the latest tag overall on Packagist at the time of testing.

No branch beyond 1.30.x allows any release before Php 8. For branches beyond 1.30.x, although the code identified above is in error, and will be corrected, it does not lead to any security exposure. That would require a `Phar::getMetadata` call, which is not present in PhpSpreadsheet. If possible and reasonable, the release notes for the fix on the other branches will include `release-note: security`.

## Reproduction

Requires Docker only, no local PHP install. Run:

```sh
bash run.sh
```

The script does the following in order: build `exploit.phar` using `php:7.4-cli` with `phar.readonly=0`, install `phpoffice/phpspreadsheet:5.7.0` through composer and run `exploit.php` on `php:8.3-cli` to show that the bypass still works against the latest tag, then install `1.30.4` and run again on `php:7.4-cli` to show the full RCE chain. All output is teed to `evidence.txt`.

`exploit.php` ships two controls. The negative control uses `phar://x/dummy.csv` to confirm that the patch still rejects the standard wrapper form. The positive control uses `phar:///work/exploit.phar/dummy.csv` to show that the three slash variant slips through. On PHP 7.4 the gadget writes the file `pwned_marker` containing the lines `WAKEUP: phpspreadsheet-bypass` and `DESTRUCT: phpspreadsheet-bypass`, which is the proof that attacker controlled code ran inside the victim process.

## Suggested fix

Do not rely on `parse_url` to detect wrappers, because its behavior depends on the slash count and on the PHP version. Either of these is safe:

```php
public static function prohibitWrappers(string $filename): void
{
    if (str_contains($filename, '://')) {
        throw new Exception("Stream wrappers are not permitted as file paths: {$filename}");
    }
}
```

Alternatively, run the path through `realpath()` first, since `realpath` returns `false` for any wrapper prefixed path.

## Files in this report
- [build-phar.php](https://github.com/user-attachments/files/27317345/build-phar.php): builds `exploit.phar` with a gadget object in its metadata.
- [exploit.php](https://github.com/user-attachments/files/27317343/exploit.php): main PoC, with the negative and positive controls.
- [exploit.phar](https://github.com/user-attachments/files/27317356/exploit.phar.txt): prebuilt phar, the gadget writes a marker when deserialized.
- [composer.json](https://github.com/user-attachments/files/27317341/composer.json): spec used by composer to install the version under test.
- [run.sh](https://github.com/user-attachments/files/27317342/run.sh): end to end reproducer through Docker.
- [evidence.txt](https://github.com/user-attachments/files/27317339/evidence.txt): log captured from the most recent `run.sh` invocation.

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-87m4-826x-3crx
- https://github.com/PHPOffice/PhpSpreadsheet
- https://github.com/advisories/GHSA-q4q6-r8wh-5cgh
