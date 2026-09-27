# [H] Craft CMS vulnerable to Remote Code Execution via unrestricted file extension 

## Summary
Severity: High
Advisory: GHSA-vqxf-r9ph-cc9c
CVE: CVE-2023-32679
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-vqxf-r9ph-cc9c
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0 <4.4.6

## Details
### Summary
Unrestricted file extension lead to a potential Remote Code Execution
(Authenticated, ALLOW_ADMIN_CHANGES=true)

### Details
#### Vulnerability Cause : 
If the name parameter value is not empty string('') in the View.php's doesTemplateExist() -> resolveTemplate() -> _resolveTemplateInternal() -> _resolveTemplate() function, it returns directly without extension verification, so that arbitrary extension files are rendered as twig templates (even if they are not extensions set in defaultTemplateExtensions = ['html', 'twig'])
```php
    /**
     * Searches for a template files, and returns the first match if there is one.
     *
     * @param string $basePath The base path to be looking in.
     * @param string $name The name of the template to be looking for.
     * @param bool $publicOnly Whether to only look for public templates (template paths that don’t start with the private template trigger).
     * @return string|null The matching file path, or `null`.
     */
    private function _resolveTemplate(string $basePath, string $name, bool $publicOnly): ?string
    {
        // Normalize the path and name
        $basePath = FileHelper::normalizePath($basePath);
        $name = trim(FileHelper::normalizePath($name), '/');

        // $name could be an empty string (e.g. to load the homepage template)
        if ($name !== '') {
            if ($publicOnly && preg_match(sprintf('/(^|\/)%s/', preg_quote($this->_privateTemplateTrigger, '/')), $name)) {
                return null;
            }

            // Maybe $name is already the full file path
            $testPath = $basePath . DIRECTORY_SEPARATOR . $name;

            if (is_file($testPath)) {
                return $testPath;
            }

            foreach ($this->_defaultTemplateExtensions as $extension) {
                $testPath = $basePath . DIRECTORY_SEPARATOR . $name . '.' . $extension;

                if (is_file($testPath)) {
                    return $testPath;
                }
            }
        }

        foreach ($this->_indexTemplateFilenames as $filename) {
            foreach ($this->_defaultTemplateExtensions as $extension) {
                $testPath = $basePath . ($name !== '' ? DIRECTORY_SEPARATOR . $name : '') . DIRECTORY_SEPARATOR . $filename . '.' . $extension;

                if (is_file($testPath)) {
                    return $testPath;
                }
            }
        }

        return null;
    }
```

When attacker with admin privileges on the DEV or Misconfigured STG, PROD, they can exploit this vulnerability to remote code execution **(ALLOW_ADMIN_CHANGES=true)**


### PoC
**Step 1)** Create a new filesystem. **Base Path: /var/www/html/templates**
![1](https://user-images.githubusercontent.com/30969523/228049254-6c3a9897-c26a-46a5-96ad-41c7b769116a.png)

**Step 2)** Create a new asset volume. **Asset Filesystem: template**
![2](https://user-images.githubusercontent.com/30969523/228049839-d2d42245-fa6e-4245-9fd2-967f1b9f4a74.png)

**Step 3)** Upload poc file( .txt , .js , .json , etc ) with twig template rce payload
```twig
{{'<pre>'}}
{{1337*1337}}
{{['cat /etc/passwd']|map('passthru')|join}}
{{['id;pwd;ls -altr /']|map('passthru')|join}}
```
![7](https://user-images.githubusercontent.com/30969523/228051307-623b78d0-4792-44ae-af0f-aff6b16f8d87.png)
![5](https://user-images.githubusercontent.com/30969523/228051064-cfaad338-3aff-4c4f-a177-9b42e473142b.png)

**Step 4)** Create a new global set with template layout. The template filename is poc.js
![8](https://user-images.githubusercontent.com/30969523/228051430-365457eb-2a10-47a8-aed9-fb400e80c6d5.png)

**Step 5)** When access global menu or /admin/global/test, poc.js is rendered as a template file and RCE confirmed
![9](https://user-images.githubusercontent.com/30969523/228053142-62a0f1ad-bbfa-4b8d-b6bd-28ed26c1cc18.png)

**Step 6)** RCE can be confirmed on other menus(Entries, Categories) where the template file is loaded.
![10](https://user-images.githubusercontent.com/30969523/228054216-5dcd0c30-85bd-4603-84e5-944cfe9ad93c.png)
![11](https://user-images.githubusercontent.com/30969523/228054146-d5a3ceea-e13d-461a-bcd6-abf260761d62.png)


**Poc Environment)** ALLOW_ADMIN_CHANGES=true, defaultTemplateExtensions=['html','twig']
![0](https://user-images.githubusercontent.com/30969523/228054764-37d78cf5-5eca-442f-873a-99e6676b8173.png)
![13](https://user-images.githubusercontent.com/30969523/228054803-1a2c40b0-e515-46b3-a653-bb5ef1a287a2.png)
![14](https://user-images.githubusercontent.com/30969523/228054821-c7b0cfd6-126a-4722-846c-26d725af1a6a.png)

### Impact
Take control of vulnerable systems, Data exfiltrations, Malware execution, Pivoting, etc.

Additionally, there are 371 domains using CraftCMS exposed on Shodan, and among them, 33 servers have "stage" or "dev" included in their hostnames. 

although the vulnerability is exploitable only in the authenticated users, configuration with ALLOW_ADMIN_CHANGES=true, there is still a potential security threat (Remote Code Execution)

![2023-03-31 10 29 53](https://user-images.githubusercontent.com/30969523/229001176-4c235b2f-e1a3-4b96-965a-78f227546a12.png)

### Remediation
Recommend taking measures by referring to https://github.com/craftcms/cms-ghsa-9f84-5wpf-3vcf/pull/1
```php
            // Maybe $name is already the full file path
            $testPath = $basePath . DIRECTORY_SEPARATOR . $name;

            if (is_file($testPath)) {
                // Remedation: Verify template file extension, before return
                $fileExt = pathinfo($testPath, PATHINFO_EXTENSION);
                $isDisallowed = false;

                if (isset($fileExt)) {
                    $isDisallowed = !in_array($fileExt, $this->_defaultTemplateExtensions);

                    if($isDisallowed) {
                        return null;
                    } else {
                        return $testPath;
                    }
                }
            }
```

![remediation](https://user-images.githubusercontent.com/30969523/228841202-43079754-0d9d-47fa-8ae3-ce5dd509796b.png)

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-vqxf-r9ph-cc9c
- https://nvd.nist.gov/vuln/detail/CVE-2023-32679
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.4.6
