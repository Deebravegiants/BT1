# [H] Mantis Bug Tracker (MantisBT) allows user account takeover in the signup/reset password process

## Summary
Severity: High
Advisory: GHSA-93x3-m7pw-ppqm
CVE: CVE-2024-34077
CWE: CWE-305, CWE-620
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-13
Source: https://github.com/advisories/GHSA-93x3-m7pw-ppqm
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.26.2

## Details
Insufficient access control in the registration and password reset process allows an attacker to reset another user's password and takeover their account, if the victim has an incomplete request pending.

The exploit is only possible while the verification token is valid, i.e for 5 minutes after the confirmation URL sent by e-mail has been opened, and the user did not complete the process by updating their password.

A brute-force attack calling account_update.php with increasing user IDs is possible. 
 
### Impact

A successful takeover would grant the attacker full access to the compromised account, including sensitive information and functionalities associated with the account, the extent of which depends on its privileges and the data it has access to.

### Patches

92d11a01b195a1b6717a2f205218089158ea6d00

### Workarounds

Mitigate the risk by reducing the verification token's validity (change the value of the `TOKEN_EXPIRY_AUTHENTICATED` constant in *constants_inc.php*).

### References

https://mantisbt.org/bugs/view.php?id=34433

### Credits

Alexander Christian, from Vantage Point Security Indonesia

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-93x3-m7pw-ppqm
- https://nvd.nist.gov/vuln/detail/CVE-2024-34077
- https://github.com/mantisbt/mantisbt/commit/92d11a01b195a1b6717a2f205218089158ea6d00
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=34433
