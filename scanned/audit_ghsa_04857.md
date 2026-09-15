# [M] Pterodactyl Panel: Client email change endpoint allows enumeration of accounts in system

## Summary
Severity: Medium
Advisory: GHSA-j7f5-gfqm-pcx3
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-j7f5-gfqm-pcx3
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.12.3

## Details
### Summary
An unprotected user enumeration vulnerability exists in the account email update endpoint, allowing authenticated users to verify whether email addresses are registered on the panel through automated requests without rate limiting or CAPTCHA protection.

### Details
The account settings page allows authenticated users to update their email address through a POST request. Unlike the login and password reset forms which implement reCAPTCHA and rate limiting protections, this endpoint lacks these safeguards entirely.
An attacker can capture the email update request (for example, using Burp Suite's proxy) and modify the email field to test arbitrary addresses. The panel's response will confirm whether each tested email is already registered in the system. Because there are no rate limits implemented, attackers can send hundreds or thousands of requests to enumerate the user base.

This is concerning because:

- The login and password reset pages correctly implement protections against enumeration
- The account page has no reCAPTCHA option available
- No rate limiting exists in the panel for this endpoint
- Authentication is required, but any valid account (including free tier/trial accounts) can exploit this

### PoC
- Log into the Pterodactyl panel with any valid account
- Navigate to Account Settings
- Open Burp Suite (or similar proxy tool) and configure your browser to proxy through it
- Attempt to change your email address and capture the POST request
- Send the captured request to Repeater
- Modify the email field to test different addresses (e.g., admin@example.com, test@example.com)
- Send multiple requests in rapid succession
- Observe the response messages which confirm whether each email exists or not 
- Repeat indefinitely without encountering rate limits or CAPTCHA challenges


### Impact
This is a user enumeration vulnerability (CWE-204: Observable Response Discrepancy).

Who is impacted:

- All Pterodactyl panel installations are affected
- Any registered user's email address can be discovered
- Particularly impacts administrators and high-value accounts

Potential consequences:

- Attackers can build a complete database of registered users
- Enumerated emails can be used for targeted phishing campaigns
- Combined with other attacks (credential stuffing, social engineering)
- Privacy violation for all users on the platform
- Competitive intelligence gathering (identifying which companies/individuals use specific panels)

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-j7f5-gfqm-pcx3
- https://github.com/pterodactyl/panel
