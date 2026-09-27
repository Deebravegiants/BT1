# [C] Command Injection in @ronomon/opened

## Summary
Severity: Critical
Advisory: GHSA-fg5w-w99f-rj6w
CVE: CVE-2021-29300
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-fg5w-w99f-rj6w
Type: github-advisory

## Affected
- npm: `@ronomon/opened` — affected >=0 <1.5.2

## Details
The @ronomon/opened library before 1.5.2 is vulnerable to a command injection vulnerability which would allow a remote attacker to execute commands on the system if the library was used with untrusted input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29300
- https://github.com/ronomon/opened/commit/7effe011d4fea8fac7f78c00615e0a6e69af68ec
- https://advisory.checkmarx.net/advisory/CX-2021-4775
- https://github.com/ronomon/opened
