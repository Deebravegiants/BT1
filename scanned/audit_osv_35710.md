# [M] Unauthenticated self-registration in MailerUp allows access to stored email data

## Summary
Severity: Medium
Advisory: CVE-2026-13164
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-13164
Type: osv

## Details
Missing Authentication for Critical Function (CWE-306) in the RegisterView (apps/accounts/views.py), exposed at POST /api/auth/register/, in MailerUp <1.0.1 allows a remote, unauthenticated attacker to self-register a working account on instances where registration is intended to be restricted, because the endpoint applies the AllowAny permission with no email verification, CAPTCHA, or administrator approval. Any account created this way can read all email stored by the instance, resulting in full disclosure of stored messages to an arbitrary unauthenticated attacker

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13164.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13164
- https://github.com/Maalfer/mailerup/commit/99eb6d4586134bf3f4422093fbf47d6794ef0ee5
- https://github.com/Maalfer/mailerup
- https://secur0.com/en/cna/cve-list/cve-2026-13164-unauthenticated-self-registration-in-mailerup-allows-access-to-stored-email-data
