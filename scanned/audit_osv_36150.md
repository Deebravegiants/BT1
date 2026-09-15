# [H] Password Reset Tokens Do Not Expire

## Summary
Severity: High
Advisory: CVE-2026-21622
Aliases: EEF-CVE-2026-21622, GHSA-6r94-pvwf-mxqm
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:H/SI:H/SA:L)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-21622
Type: osv

## Details
Insufficient Session Expiration vulnerability in hexpm hexpm/hexpm ('Elixir.Hexpm.Accounts.PasswordReset' module) allows Account Takeover.

Password reset tokens generated via the "Reset your password" flow do not expire. When a user requests a password reset, Hex sends an email containing a reset link with a token. This token remains valid indefinitely until used. There is no time-based expiration enforced.

If a user's historical emails are exposed through a data breach (e.g., a leaked mailbox archive), any unused password reset email contained in that dataset could be used by an attacker to reset the victim's password. The attacker does not need current access to the victim's email account, only access to a previously leaked copy of the reset email.

This vulnerability is associated with program files lib/hexpm/accounts/password_reset.ex and program routines 'Elixir.Hexpm.Accounts.PasswordReset':can_reset?/3.

This issue affects hexpm: from 617e44c71f1dd9043870205f371d375c5c4d886d before bb0e42091995945deef10556f58d046a52eb7884.

## References
- https://cna.erlef.org/cves/CVE-2026-21622.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-21622
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21622.json
- https://github.com/hexpm/hexpm/security/advisories/GHSA-6r94-pvwf-mxqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-21622
- https://github.com/hexpm/hexpm/commit/bb0e42091995945deef10556f58d046a52eb7884
- https://github.com/hexpm/hexpm.git
