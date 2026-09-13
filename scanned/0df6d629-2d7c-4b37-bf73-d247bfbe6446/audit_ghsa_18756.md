# [H] phpMyFAQ duplicate email registration allows multiple accounts with the same email

## Summary
Severity: High
Advisory: GHSA-9wj2-4hcm-r74j
CVE: CVE-2025-59943
CWE: CWE-284, CWE-286
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-03
Source: https://github.com/advisories/GHSA-9wj2-4hcm-r74j
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=4.0.7 <4.0.13

## Details
### Summary
phpMyFAQ does not enforce uniqueness of email addresses during user registration. This allows multiple distinct accounts to be created with the same email. Because email is often used as an identifier for password resets, notifications, and administrative actions, this flaw can cause account ambiguity and, in certain configurations, may lead to privilege escalation or account takeover.

### Details
An account management logic flaw in phpMyFAQ allows attackers to register multiple accounts under the same email address. If email is used for password reset or administrative flows, this may result in account takeover, loss of accountability, and abuse of business logic.
### PoC

1.Register  a user with email test@example.com
2.Register another user with the same email.
3.Both accounts appear in /admin/?action=user&user_action=listallusers.
<img width="1150" height="628" alt="image" src="https://github.com/user-attachments/assets/8c19f01a-e897-4ca7-b3f8-fcf83e6ff952" />

### Impact

-Data integrity loss: Multiple accounts mapped to one email break auditability.
-Password reset ambiguity: If reset flow relies on email only, attackers can target or take over accounts.
-Privilege escalation: If one account with the same email has admin privileges, an attacker controlling the email may escalate.
-Spam / DoS: Attackers can mass-register accounts with a single email to pollute the system.

This is a business logic / authentication vulnerability. Impacted users are anyone relying on phpMyFAQ’s account system where email is assumed to be unique.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-9wj2-4hcm-r74j
- https://nvd.nist.gov/vuln/detail/CVE-2025-59943
- https://github.com/thorsten/phpMyFAQ/commit/44cd20f86eb041f39d1c30a9beefad1cc61dc0ec
- https://github.com/thorsten/phpMyFAQ
