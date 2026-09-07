# [M] Vikunja has TOTP Reuse During Validity Window

## Summary
Severity: Medium
Advisory: GHSA-p747-qc5p-773r
CVE: CVE-2026-33473
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-p747-qc5p-773r
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0.13

## Details
### Summary
Any user that has enabled 2FA can have their TOTP reused during the standard 30 second validity window.

### Details
The below code is called when a user that has 2FA is authenticating to the application. Once they submit a valid username-password-totp combination, the user gets authenticated. If that same TOTP is used for the same user's account again within the validity window, it will allow the other session to authenticate successfully.

**Source**: <ins>pkg/user/totp.go:128</ins>
```go
// ValidateTOTPPasscode validated totp codes of users.
func ValidateTOTPPasscode(s *xorm.Session, passcode *TOTPPasscode) (t *TOTP, err error) {
	t, err = GetTOTPForUser(s, passcode.User)
	if err != nil {
		return
	}

	if !totp.Validate(passcode.Passcode, t.Secret) {
		return nil, ErrInvalidTOTPPasscode{Passcode: passcode.Passcode}
	}

	return
}
```

Section 6.5.1 within the [Authentication](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x15-V6-Authentication.md) section of the OWASP ASVS recommends multiple checks, some of which involving TOTPs:

> Verify that lookup secrets, out-of-band authentication requests or codes, and time-based one-time passwords (TOTPs) are only successfully usable once.

The OWASP WSTG also references this as one of their [checks](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/11-Testing_Multi-Factor_Authentication) to look for:

> Can the OTPs be used more than once?

### PoC

https://github.com/user-attachments/assets/19d3b4c3-c219-4f59-b57d-45c9f6a264c8

### Impact
Any user who uses 2FA could be impacted if their traffic is able to be captured, they're phished/social engineered, or other methods of attack. This disrupts one layer of the defense-in-depth model surrounding 2FA.

### Similar CVEs

- [CVE-2025-6014](https://nvd.nist.gov/vuln/detail/CVE-2025-6014)
- [CVE-2025-55003](https://nvd.nist.gov/vuln/detail/CVE-2025-55003)

### Remediation

Store a deny-list of TOTP codes for their validity windows and check submitted codes against it to ensure none are being reused. After their validity window has closed, the 2FA code can be removed from the list.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-p747-qc5p-773r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33473
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.0-was-released
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
