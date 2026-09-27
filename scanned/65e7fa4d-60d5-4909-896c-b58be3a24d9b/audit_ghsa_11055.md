# [H] INSATutorat has an authorization bypass vulnerability in its  /api/admin/* endpoints

## Summary
Severity: High
Advisory: GHSA-xfx2-prg5-jq3g
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-01
Source: https://github.com/advisories/GHSA-xfx2-prg5-jq3g
Type: github-advisory

## Affected
- Go: `github.com/romitou/insatutorat` — affected >=0 <0.0.0-20260226075457-15ae47425aed

## Details
### Impact

An authorization bypass vulnerability was discovered in the administration pages of the tutoring application. When a standard user (logged in but without administrator privileges) attempts to access a resource under /api/admin/, the system detects the error but does not block the request.

As a result, sensitive data is still transmitted by the server in the request (GET), and modification actions such as campaign creation (POST) are executed successfully despite the FORBIDDEN error message. All /api/admin/* endpoints are affected.

### Remediation

The issue was resolved by adding the missing c.Abort() instruction in the Gin authentication middleware (commit 15ae474). This instruction immediately interrupts the processing chain if the user is not an administrator.

### Workarounds

There is no workaround other than applying the fix in the source code.

### Resources:
* Link to the fix commit: [15ae474](https://github.com/Romitou/INSATutorat/commit/15ae47425aed337181f7a6c54a9d199c93b041eb)


### Credits
INSATutorat thanks the Master 2 SSI 25-26 team at the University of Rouen Normandie for their research work on this project.
- Malak Bekkai
- Matthieu Espada Mora
- Amen Allah Khalf Allah
- Liam Laouenan
- Neila Ould Slimane
- Lucas Thomire

This advisory was translated from French to English by GitHub Copilot.

## References
- https://github.com/Romitou/INSATutorat/security/advisories/GHSA-xfx2-prg5-jq3g
- https://github.com/Romitou/INSATutorat/commit/15ae47425aed337181f7a6c54a9d199c93b041eb
- https://github.com/Romitou/INSATutorat
