# [M] sftpgo vulnerable to brute force takeover of OpenID Connect session cookies

## Summary
Severity: Medium
Advisory: GHSA-6943-qr24-82vx
CVE: CVE-2024-52801
CWE: CWE-327
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-6943-qr24-82vx
Type: github-advisory

## Affected
- Go: `github.com/drakkan/sftpgo/v2` — affected >=2.3.0 <2.6.4

## Details
### Impact

The OpenID Connect implementation, in the affected SFTPGo versions, allows authenticated users to brute force session cookies and thereby gain access to other users' data, since the cookies are generated predictably using the [xid](https://github.com/rs/xid) library and are therefore unique but not cryptographically secure.

### Patches

This issue was fixed in version v2.6.4, where cookies are opaque and cryptographically secure strings.

### References

https://github.com/drakkan/sftpgo/commit/f30a9a2095bf90c0661b04fe038e3b7efc788bc6

## References
- https://github.com/drakkan/sftpgo/security/advisories/GHSA-6943-qr24-82vx
- https://nvd.nist.gov/vuln/detail/CVE-2024-52801
- https://github.com/drakkan/sftpgo/commit/f30a9a2095bf90c0661b04fe038e3b7efc788bc6
- https://github.com/drakkan/sftpgo
- https://github.com/rs/xid
