# [H] Memos' Access Tokens Stay Valid after User Password Change

## Summary
Severity: High
Advisory: GHSA-mr34-8733-grr2
CVE: CVE-2024-21635
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-mr34-8733-grr2
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.18.2

## Details
### Summary
Access Tokens are used to authenticate application access. When a user changes their password, the existing list of Access Tokens stay valid instead of expiring. If a user finds that their account has been compromised, they can update their password. 

The bad actor though will still have access to their account because the bad actor's Access Token stays on the list as a valid token. The user will have to manually delete the bad actor's Access Token to secure their account. The list of Access Tokens has a generic Description which makes it hard to pinpoint a bad actor in a list of Access Tokens. 

### Details

To improve Memos security, all Access Tokens will need to be revoked when a user changes their password. This removes the session for all the user's devices and prompts the user to log in again. You can treat the old Access Tokens as "invalid" because those Access Tokens were created with the older password.

### PoC

1. Have 2 devices on hand
2. Log onto your Memos account on both devices. Notice how Access Tokens are created for each.
3. On one device, successfully change the password. Refresh the page on the 2nd device and notice how it doesn't log out the user.
4. On the 2nd device, change the password again. Refresh the page on the 1st device and notice how it doesn't log out the user.

### Impact

A bad actor will still have access to the user's account because the Access Token does not expire on a password update. Having multi-factor authentication will vastly improve account security in Account Takeover cases instead of just relying on a password.

## References
- https://github.com/usememos/memos/security/advisories/GHSA-mr34-8733-grr2
- https://nvd.nist.gov/vuln/detail/CVE-2024-21635
- https://github.com/usememos/memos
- https://github.com/usememos/memos/releases/tag/v0.18.2
- https://owasp.org/Top10/A04_2021-Insecure_Design
- http://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures
