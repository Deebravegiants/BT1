# [H] Local File System Validation Bypass Leading to File Overwrite, Sensitive File Access, and Potential Code Execution

## Summary
Severity: High
Advisory: GHSA-jrh5-vhr9-qh7q
CVE: CVE-2024-52291
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-jrh5-vhr9-qh7q
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.4.6
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.12.5

## Details
### Summary
A vulnerability in CraftCMS allows an attacker to bypass local file system validation by utilizing a double `file://` scheme (e.g., `file://file:////`). This enables the attacker to specify sensitive folders as the file system, leading to potential file overwriting through malicious uploads, unauthorized access to sensitive files, and, under certain conditions, remote code execution (RCE) via Server-Side Template Injection (SSTI) payloads.

Note that this will only work if you have an authenticated administrator account with [allowAdminChanges enabled](https://craftcms.com/docs/5.x/reference/config/general.html#allowadminchanges).

https://craftcms.com/knowledge-base/securing-craft#set-allowAdminChanges-to-false-in-production

### Details
The issue lies in line 57 of `cms/src/helpers/FileHelper.php`, it only removes `file://` on the most left. It is trivial to bypass this sanitization by adding 2 `file://`, e.g. `file://file:////`.
```php
    public static function normalizePath($path, $ds = DIRECTORY_SEPARATOR): string
    {
        // Remove any file protocol wrappers
        $path = StringHelper::removeLeft($path, 'file://');

        // Is this a UNC network share path?
        $isUnc = (str_starts_with($path, '//') || str_starts_with($path, '\\\\'));

        // Normalize the path
        $path = parent::normalizePath($path, $ds);

        // If it is UNC, add those slashes back in front
        if ($isUnc) {
            $path = $ds . $ds . ltrim($path, $ds);
        }

        return $path;
    }
```

### PoC
1. Sign in with an admin account and navigate to `Settings → Assets`, then create a new volume.
2. n the Asset Filesystem section, create a new file system and set the Base Path to `file://file:////vendor`.
Without the prefix, the selection fails.
 ![alt text](https://winslow1984.com/uploads/images/gallery/2024-09/1.png)
With the double `file://` prefix, the selection succeeds.
 ![alt text](https://winslow1984.com/uploads/images/gallery/2024-09/2.png)
3. Access Assets from the left navigation bar, then upload a file into this volume.
 ![alt text](https://winslow1984.com/uploads/images/gallery/2024-09/3.png)
4. The file is successfully uploaded and stored in the sensitive folder specified (e.g., `/vendor`).
 ![alt text](https://winslow1984.com/uploads/images/gallery/2024-09/4.png)
5. SSTI payloads can be uploaded to `/templates` folder, though full code execution was not achieved during testing, some payloads were still successful, leading to sensitive information disclosure, among other potential impacts.
 ![alt text](https://winslow1984.com/uploads/images/gallery/2024-09/7306f23f208e8e8dff48d65a0dc02dc.png)

### Impact
Attackers who compromise an admin account(The admin user is not equal to the server owner) can exploit this flaw to assign sensitive folders as the base path of the filesystem. For instance, if the path `/templates` is specified (e.g., `file://file:////var/www/html/templates`), the attacker could upload SSTI payloads. While CraftCMS includes strict SSTI input sanitization, RCE may still be possible if the attacker can craft a valid payload, as seen in similar vulnerabilities (e.g., [GHSA-44wr-rmwq-3phw](https://github.com/advisories/GHSA-44wr-rmwq-3phw)).

Additionally, attackers can upload tampered files to overwrite critical web application files. By enabling public URLs for files in the specified filesystem, they can also retrieve sensitive files (e.g., configuration files from the local file system).

Although the vulnerability is exploitable only in the authenticated users, configuration with `ALLOW_ADMIN_CHANGES=true`, there is still a potential security threat.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-jrh5-vhr9-qh7q
- https://nvd.nist.gov/vuln/detail/CVE-2024-52291
- https://github.com/craftcms/cms
