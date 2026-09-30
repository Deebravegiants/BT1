# [M] Grav Admin Plugin vulnerable to User Enumeration & Email Disclosure

## Summary
Severity: Medium
Advisory: GHSA-q3qx-cp62-f6m7
CVE: CVE-2025-66307
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-q3qx-cp62-f6m7
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
# Grav v1.7.49.5 / Admin v1.10.49.1 – User Enumeration & Email Disclosure

### Summary
A **user enumeration and email disclosure vulnerability** exists in Grav **v1.7.49.5** with Admin plugin **v1.10.49.1**.  
The "Forgot Password" functionality at `/admin/forgot` leaks information about valid usernames and their associated email addresses through distinct server responses.  
This allows an attacker to enumerate users and disclose sensitive email addresses, which can be leveraged for targeted attacks such as password spraying, phishing, or social engineering.  

### Details

The issue resides in the [`taskForgot()`](https://github.com/getgrav/grav-plugin-admin/blob/6d673fc7c4f6962756f93ae651371e81f7f20924/classes/plugin/Controllers/Login/LoginController.php#L349) function, which handles the forgot password workflow.  
Relevant vulnerable logic:

```php
if (null === $user || $user->state !== 'enabled' || !$to) {
    ...
    // Generic message for invalid/non-existing users
    $this->setMessage($this->translate('PLUGIN_ADMIN.FORGOT_INSTRUCTIONS_SENT_VIA_EMAIL'));
    return $this->createRedirectResponse($current);
}

if ($rateLimiter->isRateLimited($username)) {
    ...
    $interval = $config->get('plugins.login.max_pw_resets_interval', 2);

    // Sensitive message for valid users
    $this->setMessage($this->translate('PLUGIN_LOGIN.FORGOT_CANNOT_RESET_IT_IS_BLOCKED', $to, $interval), 'error');

    return $this->createRedirectResponse($current);
}
```

When an attacker submits the password reset form at `/admin/forgot` with an **invalid username**, the application responds with:  

```
Instructions to reset your password have been sent to your email address
```

However, when a **valid username** is supplied, and the attacker repeatedly triggers password reset requests, the application responds with:  

```
Cannot reset password for <USER_EMAIL>, password reset functionality temporarily blocked, please try later (maximum 60 minutes)
```

This discrepancy in responses enables:  
1. **User Enumeration** – Attackers can determine if a username exists in the system by analyzing the response.  
2. **User Email Disclosure** – The system discloses the actual email address associated with the account (e.g., `admin@localhost.test`).  

This violates best practices for authentication flows, where responses should remain generic to avoid leaking sensitive information.

### PoC
1. Navigate to the **Forgot Password** page:  `https://<target>/admin/forgot`
1. Submit a reset request with a random/invalid username (e.g., `invalid_user`):  

- Response:  
  ```
  Instructions to reset your password have been sent to your email address
  ```
3. Submit a reset request with a valid username (e.g., `admin`).  
4. Repeatedly request a reset for the same username until the lockout mechanism triggers.  
- Response:  
  ```
  Cannot reset password for admin@localhost.test, password reset functionality temporarily blocked, please try later (maximum 60 minutes)
  ```
5. Observe the leaked **email address** of the admin account in the error message.  

### Impact
- **Severity:** Medium  
- **Type:** Information Disclosure / User Enumeration  
- **Who is Impacted:** All Grav sites using Admin plugin **v1.10.49.1** with password reset enabled.  
- **Risks:**  
  - Allows attackers to enumerate valid usernames.  
  - Exposes email addresses of admin accounts, which can be used in:  
  - Credential stuffing  
  - Password spraying  
  - Phishing/social engineering campaigns  
  - Further exploitation in combination with other vulnerabilities  


### Recommendation

- Modify the [`taskForgot()`](https://github.com/getgrav/grav-plugin-admin/blob/6d673fc7c4f6962756f93ae651371e81f7f20924/classes/plugin/Controllers/Login/LoginController.php#L349) logic to always return a generic, non-identifying message, regardless of whether the username exists or rate limits are hit.

- Example safe response:
  ```ini
  If the account exists, password reset instructions will be sent.
  ```

- Do not include email addresses ($to) or other sensitive data in error messages.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-q3qx-cp62-f6m7
- https://nvd.nist.gov/vuln/detail/CVE-2025-66307
- https://github.com/getgrav/grav-plugin-admin/commit/99f653296504f1d6408510dd2f6f20a45a26f9b0
- https://github.com/getgrav/grav
- https://github.com/getgrav/grav-plugin-admin/blob/6d673fc7c4f6962756f93ae651371e81f7f20924/classes/plugin/Controllers/Login/LoginController.php#L349
