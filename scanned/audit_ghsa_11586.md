# [H] Craft CMS has unauthenticated activation email trigger with potential user enumeration

## Summary
Severity: High
Advisory: GHSA-234q-vvw3-mrfq
CVE: CVE-2026-29069
CWE: CWE-287, CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-234q-vvw3-mrfq
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.0-beta.2
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.0-beta.2

## Details
The `actionSendActivationEmail()` endpoint is accessible to unauthenticated users and does not require a permission check for pending users. An attacker with no prior access can trigger activation emails for any pending user account by knowing or guessing the user ID. If the attacker controls the target user’s email address, they can activate the account and gain access to the system.

The vulnerability is not that anonymous access exists - there’s a legitimate use case for it. The vulnerability is that the endpoint accepts arbitrary `userId` parameters without verifying ownership.

Craft CMS allows public user registration. When a user registers but doesn’t receive their activation email (spam filter, typo correction, etc.), they need a way to request a resend. This is why `send-activation-email` is in the `allowAnonymous` array - it’s intentional self-service functionality.

### The Security Gap

The endpoint accepts `userId` as the identifier:
```php
$userId = $this->request->getRequiredBodyParam('userId');
```

This allows any visitor to trigger activation emails for any pending user, not just their own registration.

---

## Background

When administrators create new user accounts in Craft CMS, users are created in a “pending” state until they activate their account via an emailed link. The `actionSendActivationEmail()` function sends (or resends) this activation email.

**Expected Behavior:** Anonymous users should only be able to resend activation emails for their own registration.

**Actual Behavior:**
1. The endpoint is listed in `allowAnonymous` - no login required (intentional for self-service)
2. For pending users, there is NO ownership verification
3. Any unauthenticated visitor can trigger activation emails for ANY pending user by ID

---

## Attack Scenarios

### Scenario 1: Targeted Account Takeover

**Prerequisites:** Attacker controls target user’s email (compromised email, shared mailbox, typosquatting, etc.)

```
1. Admin creates a user account for victim@company.com
2. User account is in PENDING state (hasn’t activated yet)
3. Attacker has compromised victim@company.com (or it’s a typo of attacker’s domain)
4. Attacker discovers user ID (brute-force, GraphQL enumeration, or insider knowledge)
5. Attacker (unauthenticated) triggers: POST /actions/users/send-activation-email
6. Activation email sent to victim@company.com (attacker-controlled)
7. Attacker clicks activation link, sets password
8. Attacker gains access as that user with pre-assigned permissions
```

### Scenario 2: User ID Brute-Force Enumeration

```
1. Attacker iterates through user IDs (1, 2, 3, ...)
2. For each ID, the attacker calls send-activation-email
3. Response reveals user state:
   - "Activation email sent." = Pending user exists
   - "User not found" = No user with this ID
   - "Activation emails can only be sent to inactive or pending users" = Active user exists
4. Attacker builds a map of all user IDs and their states
5. For any pending user whose email an attacker controls → account takeover
```

### Scenario 3: GraphQL + Targeted Attack

**Prerequisites:** GraphQL public schema allows user queries

```
1. Attacker queries GraphQL: { users { id email status } }
2. Filters for pending users
3. Cross-references with emails attacker controls
4. Triggers activation for the target user
5. Account takeover
```

### Scenario 4: Email Spam / Harassment

```
1. Attacker brute-forces all pending user IDs
2. Repeatedly triggers activation emails
3. Victims receive unwanted emails from the Craft site
4. Potential for:
   - Reputation damage to the site
   - Email deliverability issues (spam reports)
   - User confusion/phishing vector
```

---

## References

https://github.com/craftcms/cms/commit/c3d02d4a7246f516933f42106c0a67ce062f68d8

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-234q-vvw3-mrfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-29069
- https://github.com/craftcms/cms/commit/c3d02d4a7246f516933f42106c0a67ce062f68d8
- https://github.com/craftcms/cms
