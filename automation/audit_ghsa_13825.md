# [H] OroPlatform vulnerable to path traversal during temporary file manipulations

## Summary
Severity: High
Advisory: GHSA-9v3j-4j64-p937
CVE: CVE-2022-41951
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-9v3j-4j64-p937
Type: github-advisory

## Affected
- Packagist: `oro/platform` — affected >=4.1.0
- Packagist: `oro/platform` — affected >=4.2.0
- Packagist: `oro/platform` — affected >=5.0.0 <5.0.8

## Details
### Impact
Path Traversal is possible in `Oro\Bundle\GaufretteBundle\FileManager::getTemporaryFileName`. 
With this method, an attacker can pass the path to a non-existent file, which will allow writing the content to a new file that will be available during script execution. The file will be deleted immediately after the script ends. 

### Workarounds
Apply patch
```patch
--- a/vendor/oro/platform/src/Oro/Bundle/GaufretteBundle/FileManager.php
+++ b/vendor/oro/platform/src/Oro/Bundle/GaufretteBundle/FileManager.php
@@ -614,6 +614,10 @@
      */
     public function getTemporaryFileName(string $suggestedFileName = null): string
     {
+        if ($suggestedFileName) {
+            $suggestedFileName = basename($suggestedFileName);
+        }
+
         $tmpDir = ini_get('upload_tmp_dir');
         if (!$tmpDir || !is_dir($tmpDir) || !is_writable($tmpDir)) {
             $tmpDir = sys_get_temp_dir();

```

Or decorate `Oro\Bundle\GaufretteBundle\FileManager::getTemporaryFileName` in your customization and clear `$suggestedFileName` argument

```php
    public function getTemporaryFileName(string $suggestedFileName = null): string
    {
        if ($suggestedFileName) {
            $suggestedFileName = basename($suggestedFileName);
        }

        return parent::getTemporaryFileName($suggestedFileName);
    }
```

### References
 - [Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
 - [How to Decorate Services](https://symfony.com/doc/5.4/service_container/service_decoration.html)

## References
- https://github.com/oroinc/platform/security/advisories/GHSA-9v3j-4j64-p937
- https://nvd.nist.gov/vuln/detail/CVE-2022-41951
- https://github.com/oroinc/platform
