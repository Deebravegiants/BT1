# [H] ZITADEL's Improper Lockout Mechanism Leads to MFA Bypass

## Summary
Severity: High
Advisory: GHSA-7j7j-66cv-m239
CVE: CVE-2024-32868
CWE: CWE-287, CWE-297, CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-7j7j-66cv-m239
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=0 <2.50.0

## Details
### Impact
ZITADEL provides users the possibility to use Time-based One-Time-Password (TOTP) and One-Time-Password (OTP) through SMS and Email.

While ZITADEL already gives administrators the option to define a `Lockout Policy` with a maximum amount of failed password check attempts, there was no such mechanism for (T)OTP checks.

### Patches
2.x versions are fixed on >= [2.50.0](https://github.com/zitadel/zitadel/releases/tag/v2.50.0)

### Workarounds
There is no workaround since a patch is already available.

### References
None

### Questions
If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

Thanks to Jack Moran from Layer 9 Information Security, Ethan from zxsecurity and Amit Laish from GE Vernova for finding and reporting the vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-7j7j-66cv-m239
- https://nvd.nist.gov/vuln/detail/CVE-2024-32868
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.50.0
