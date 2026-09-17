# [H] OpenC3 COSMOS: Hijacked session token can be used to reset password for persistence

## Summary
Severity: High
Advisory: GHSA-wgx6-g857-jjf7
CVE: CVE-2026-42084
CWE: CWE-620
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-wgx6-g857-jjf7
Type: github-advisory

## Affected
- RubyGems: `openc3` — affected >=0 <6.10.5
- RubyGems: `openc3` — affected >=7.0.0.pre.rc1 <7.0.0-rc3

## Details
### Summary
The OpenC3 password change functionality allows a user to change their password without providing the old password, by accepting a valid session token instead. In assumed breach scenarios, this behaviour can be exploited by an attacker who has already obtained a valid session token, to gain persistence in hijacked account (including admin) and prevent legitimate users from accessing the account.

### Details
The design flaw in authentication model ([authentication.rb](https://github.com/OpenC3/cosmos/blob/397abec0d57972881a2e8dc10902d0dce9c27f42/openc3/lib/openc3/utilities/authentication.rb)) allows for interchangeable use of password and session tokens for user authentication As old tokens are not revoked upon password reset, an attacker who has obtained a valid session token can continue to authenticate and change the account’s password even after the victim resets it, thereby maintaining persistent control over the compromised account.

### PoC
1. Attacker is logged in user account with hijacked valid session token, but not knowing the actual password
2. Legitimate user, as preventive action, changes his password (_password123_) using old password (_password_), that he knows, then establishes new session
3. Attacker issues another password change request (in web proxy like Burp) supplying his still valid token as _old_password_, changing it to attacker-password, from this point preventing any other legitimate users from accessing account
<img width="912" height="479" alt="image" src="https://github.com/user-attachments/assets/d27b5980-0326-40f8-bb39-657d7b1c95a0" />
<img width="923" height="423" alt="image" src="https://github.com/user-attachments/assets/060d9fe1-637e-4a2d-9142-76612984ea28" />

### Impact
Persistence of an attacker who obtained valid session token and preventing legitimate users from account access

## References
- https://github.com/OpenC3/cosmos/security/advisories/GHSA-wgx6-g857-jjf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-42084
- https://github.com/OpenC3/cosmos/commit/2e623714e3426d5ae81b6f8239d4a2a6937ef776
- https://github.com/OpenC3/cosmos
- https://github.com/OpenC3/cosmos/releases/tag/v6.10.5
- https://github.com/OpenC3/cosmos/releases/tag/v7.0.0-rc3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openc3/CVE-2026-42084.yml
