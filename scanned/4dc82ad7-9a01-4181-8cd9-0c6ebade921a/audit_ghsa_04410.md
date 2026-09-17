# [H] Laravel Framework: CRLF injection in default email rule 

## Summary
Severity: High
Advisory: GHSA-5vg9-5847-vvmq
CWE: CWE-93
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-5vg9-5847-vvmq
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=13.0.0 <13.10.0
- Packagist: `laravel/framework` — affected >=0 <12.60.0

## Details
## Summary
A CRLF injection vulnerability in Laravel's email validation, in combination with how Symfony Mailer and Symfony Mime handle certain character sequences, may allow an unauthenticated attacker to interfere with outbound email processing in applications that send mail to user-supplied addresses.

## Description
Laravel applications that send email to addresses provided by users — for example during authentication flows or contact forms — may be vulnerable to manipulation of outbound mail content if the address is not adequately sanitized before it reaches the mail transport layer.
An attacker who can supply an email address to such a flow may, under certain conditions, be able to influence the content of emails sent by the application, cause those emails to be delivered to unintended recipients, or cause the application's mail server to send unintended messages.

## Impact
Affected applications may be exposed to unauthorized access and mail relay abuse. The severity depends on what the application sends by email and how its mail infrastructure is configured.

## Remediation
Upgrade to version 12.60.0 or later, or 13.10.0 or later.

## References
- https://github.com/laravel/framework/security/advisories/GHSA-5vg9-5847-vvmq
- https://github.com/laravel/framework
