# [H] phpMyFAQ has SQL Injection in CurrentUser::setTokenData through unescaped OAuth token fields

## Summary
Severity: High
Advisory: GHSA-pm8c-3qq3-72w7
CVE: CVE-2026-46359
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-pm8c-3qq3-72w7
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

`CurrentUser::setTokenData()` in `phpmyfaq/src/phpMyFAQ/User/CurrentUser.php` at lines 515-534 builds a SQL UPDATE statement with `sprintf` and interpolates OAuth token fields (`refresh_token`, `access_token`, `code_verifier`, and `json_encode($token['jwt'])`) without calling `$db->escape()`. Sibling methods `setAuthSource()` and `setRememberMe()` in the same file do call `$db->escape()` on user-controlled values, so the omission is local to this method. An attacker (Bob) whose Azure AD display name contains a single quote (for example `O'Brien`, or a deliberate SQL payload) breaks out of the string literal and injects arbitrary SQL against the phpMyFAQ database.

## Details

**Vulnerable code** (`phpmyfaq/src/phpMyFAQ/User/CurrentUser.php`, lines 513-534):

```php
public function setTokenData(#[\SensitiveParameter] array $token): bool
{
    $update = sprintf(
        "
        UPDATE
            %sfaquser
        SET
            refresh_token = '%s',
            access_token = '%s',
            code_verifier = '%s',
            jwt = '%s'
        WHERE
            user_id = %d",
        Database::getTablePrefix(),
        $token['refresh_token'],
        $token['access_token'],
        $token['code_verifier'],
        json_encode($token['jwt'], JSON_THROW_ON_ERROR),
        $this->getUserId(),
    );

    return (bool) $this->configuration->getDb()->query($update);
}
```

`json_encode()` does NOT escape single quotes. A JWT claim such as `{"preferred_username": "O'Malley"}` produces `{"preferred_username":"O'Malley"}` after `json_encode`, which terminates the SQL string literal at the apostrophe.

**Correct pattern in the same file** (`setAuthSource`, line 458-461):

```php
$update = sprintf(
    "UPDATE %sfaquser SET auth_source = '%s' WHERE user_id = %d",
    Database::getTablePrefix(),
    $this->configuration->getDb()->escape($authSource),
    $this->getUserId(),
);
```

`setRememberMe()` (line 471-478) follows the same safe pattern with `$db->escape()`.

**Reachability**: The phpMyFAQ Azure AD (Entra ID) OAuth flow calls `setTokenData()` after token exchange. The token response includes an `id_token` whose payload originates from the identity provider. An attacker registers a Microsoft account with a display name or custom claim containing SQL metacharacters. When that user logs into a phpMyFAQ instance with Azure AD auth enabled, the malicious claim flows into the UPDATE without sanitization.

## Proof of Concept

Prerequisites: phpMyFAQ instance with Azure AD / Entra ID authentication enabled.

1. Bob registers an Azure AD account with display name `x]","email":"x',(SELECT SLEEP(5)))-- -`.

2. Bob initiates the OAuth login flow on the target phpMyFAQ.

3. After authorization, the token endpoint returns a JWT with the crafted claim.

4. phpMyFAQ calls `setTokenData()` with the unsanitized token array. The resulting SQL becomes:

```sql
UPDATE faquser
SET
    refresh_token = '<valid>',
    access_token = '<valid>',
    code_verifier = '<valid>',
    jwt = '{"preferred_username":"x',(SELECT SLEEP(5)))-- -"}'
WHERE
    user_id = 42
```

The single quote after `x` closes the `jwt` string literal. Everything after it executes as attacker-controlled SQL.

5. To confirm time-based blind injection locally (requires modifying the OAuth token response in a proxy):

```python
import requests

# Simulates what happens when the crafted JWT claim reaches the DB
# In production, this happens automatically through the OAuth flow
payload = "x'||(SELECT SLEEP(5))||'"

# The interpolated query will pause for 5 seconds, confirming injection
print(f"Injected jwt value: {payload}")
print("If the login takes 5+ seconds longer than normal, injection succeeded.")
```

## Impact

An attacker who can authenticate via Azure AD with a crafted claim achieves arbitrary SQL execution on the phpMyFAQ database. This permits reading all FAQ data (including restricted entries), modifying or deleting content, and extracting password hashes and session tokens of all users including administrators.

**CWE**: CWE-89 (SQL Injection)

## Recommended Fix

Escape all interpolated values using `$this->configuration->getDb()->escape()`, matching the pattern used by `setAuthSource()` and `setRememberMe()` in the same file:

```php
public function setTokenData(#[\SensitiveParameter] array $token): bool
{
    $db = $this->configuration->getDb();
    $update = sprintf(
        "
        UPDATE
            %sfaquser
        SET
            refresh_token = '%s',
            access_token = '%s',
            code_verifier = '%s',
            jwt = '%s'
        WHERE
            user_id = %d",
        Database::getTablePrefix(),
        $db->escape($token['refresh_token']),
        $db->escape($token['access_token']),
        $db->escape($token['code_verifier']),
        $db->escape(json_encode($token['jwt'], JSON_THROW_ON_ERROR)),
        $this->getUserId(),
    );

    return (bool) $db->query($update);
}
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-pm8c-3qq3-72w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-46359
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-sql-injection-in-currentuser-settokendata-via-unescaped-oauth-token-fields
