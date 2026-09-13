# [M] Shopware has user enumeration via distinct error codes on Store API login endpoint

## Summary
Severity: Medium
Advisory: GHSA-gqc5-xv7m-gcjq
CVE: CVE-2026-31888
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-gqc5-xv7m-gcjq
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.8.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.14
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.8.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.15

## Details
## Summary

The Store API login endpoint (`POST /store-api/account/login`) returns different error codes depending on whether the submitted email address belongs to a registered customer (`CHECKOUT__CUSTOMER_AUTH_BAD_CREDENTIALS`) or is unknown (`CHECKOUT__CUSTOMER_NOT_FOUND`). The "not found" response also echoes the probed email address. This allows an unauthenticated attacker to enumerate valid customer accounts. The storefront login controller correctly unifies both error paths, but the Store API does not — indicating an inconsistent defense.

## CWE

- **CWE-204**: Observable Response Discrepancy

## Description

### Distinct error codes leak account existence

The login flow in `AccountService::getCustomerByLogin()` calls `getCustomerByEmail()` first, which throws `CustomerNotFoundException` if the email is not found. If the email IS found but the password is wrong, a separate `BadCredentialsException` is thrown:

```php
// src/Core/Checkout/Customer/SalesChannel/AccountService.php:116-145
public function getCustomerByLogin(string $email, string $password, SalesChannelContext $context): CustomerEntity
{
    if ($this->isPasswordTooLong($password)) {
        throw CustomerException::badCredentials();
    }

    $customer = $this->getCustomerByEmail($email, $context);
    // ↑ Throws CustomerNotFoundException with CHECKOUT__CUSTOMER_NOT_FOUND if email unknown

    if ($customer->hasLegacyPassword()) {
        if (!$this->legacyPasswordVerifier->verify($password, $customer)) {
            throw CustomerException::badCredentials();
            // ↑ Throws BadCredentialsException with CHECKOUT__CUSTOMER_AUTH_BAD_CREDENTIALS
        }
        // ...
    }

    if ($customer->getPassword() === null
        || !password_verify($password, $customer->getPassword())) {
        throw CustomerException::badCredentials();
        // ↑ Same: CHECKOUT__CUSTOMER_AUTH_BAD_CREDENTIALS
    }
    // ...
}
```

The two exception types produce clearly distinguishable API responses:

**Email not registered:**
```json
{
  "errors": [{
    "status": "401",
    "code": "CHECKOUT__CUSTOMER_NOT_FOUND",
    "detail": "No matching customer for the email \"probe@example.com\" was found.",
    "meta": { "parameters": { "email": "probe@example.com" } }
  }]
}
```

**Email registered, wrong password:**
```json
{
  "errors": [{
    "status": "401",
    "code": "CHECKOUT__CUSTOMER_AUTH_BAD_CREDENTIALS",
    "detail": "Invalid username and/or password."
  }]
}
```

### Storefront is protected — Store API is not

The storefront login controller demonstrates that Shopware's developers are aware of this risk class. `AuthController::login()` catches both exceptions together and returns a generic error:

```php
// src/Storefront/Controller/AuthController.php:203
} catch (BadCredentialsException|CustomerNotFoundException) {
    // Unified handling — no distinction exposed to the user
}
```

The Store API `LoginRoute::login()` does NOT catch these exceptions. They propagate to the global `ErrorResponseFactory`, which serializes the distinct error codes into the JSON response:

```php
// src/Core/Checkout/Customer/SalesChannel/LoginRoute.php:54-58
$token = $this->accountService->loginByCredentials(
    $email,
    (string) $data->get('password'),
    $context
);
// No try/catch — exceptions propagate with distinct codes
```

This inconsistency confirms the Store API exposure is an oversight, not a design decision.

### Rate limiting is present but insufficient for enumeration

The login route has rate limiting (LoginRoute.php:47-51) keyed on `strtolower($email) . '-' . $clientIp`. This slows bulk enumeration but does not prevent it because:

1. The attacker only needs **one request per email** to determine existence
2. The rate limit key includes the IP, so rotating IPs resets the counter
3. The rate limiter is designed to prevent brute-force password guessing, not single-probe enumeration

## Impact

- **Customer email enumeration**: An attacker can confirm whether specific email addresses are registered as customers, enabling targeted attacks
- **Phishing enablement**: Confirmed customer emails can be targeted with store-specific phishing campaigns (e.g., fake order confirmations, password reset lures)
- **Credential stuffing optimization**: Attackers with breached credential databases can first filter for valid emails before attempting password guesses, improving efficiency against rate limits
- **Privacy violation**: Confirms an individual's association with a specific store, which may be sensitive depending on the store's nature (e.g., medical supplies, adult products)
- **Email reflection**: The `CHECKOUT__CUSTOMER_NOT_FOUND` response echoes the probed email in the `detail` and `meta.parameters.email` fields, which could be leveraged in reflected content attacks

## Recommended Remediation

### Option 1: Catch both exceptions in LoginRoute and throw a unified error (Preferred)

Apply the same pattern already used in the storefront controller:

```php
// src/Core/Checkout/Customer/SalesChannel/LoginRoute.php
public function login(#[\SensitiveParameter] RequestDataBag $data, SalesChannelContext $context): ContextTokenResponse
{
    EmailIdnConverter::encodeDataBag($data);
    $email = (string) $data->get('email', $data->get('username'));

    if ($this->requestStack->getMainRequest() !== null) {
        $cacheKey = strtolower($email) . '-' . $this->requestStack->getMainRequest()->getClientIp();

        try {
            $this->rateLimiter->ensureAccepted(RateLimiter::LOGIN_ROUTE, $cacheKey);
        } catch (RateLimitExceededException $exception) {
            throw CustomerException::customerAuthThrottledException($exception->getWaitTime(), $exception);
        }
    }

    try {
        $token = $this->accountService->loginByCredentials(
            $email,
            (string) $data->get('password'),
            $context
        );
    } catch (CustomerNotFoundException) {
        // Normalize to the same exception as bad credentials
        throw CustomerException::badCredentials();
    }

    if (isset($cacheKey)) {
        $this->rateLimiter->reset(RateLimiter::LOGIN_ROUTE, $cacheKey);
    }

    return new ContextTokenResponse($token);
}
```

This ensures both "not found" and "bad credentials" return the same `CHECKOUT__CUSTOMER_AUTH_BAD_CREDENTIALS` code and generic message.

### Option 2: Unify at the AccountService layer

For defense in depth, change `AccountService::getCustomerByLogin()` to throw `BadCredentialsException` instead of letting `CustomerNotFoundException` propagate:

```php
// src/Core/Checkout/Customer/SalesChannel/AccountService.php
public function getCustomerByLogin(string $email, string $password, SalesChannelContext $context): CustomerEntity
{
    if ($this->isPasswordTooLong($password)) {
        throw CustomerException::badCredentials();
    }

    try {
        $customer = $this->getCustomerByEmail($email, $context);
    } catch (CustomerNotFoundException) {
        throw CustomerException::badCredentials();
    }

    // ... rest of password verification
}
```

This protects all callers of `getCustomerByLogin()` regardless of how they handle exceptions. Note: `getCustomerByEmail()` is also called independently (e.g., password recovery), so that method should continue to throw `CustomerNotFoundException` for internal use — the normalization should happen at the login boundary.

### Additional: Fix registration endpoint

The registration endpoint (`POST /store-api/account/register`) also leaks email existence via `CUSTOMER_EMAIL_NOT_UNIQUE`. For complete remediation, consider returning a generic success response and sending a notification email to the existing address instead.

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-gqc5-xv7m-gcjq
- https://nvd.nist.gov/vuln/detail/CVE-2026-31888
- https://github.com/shopware/shopware
