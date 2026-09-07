# [M] CRLF Injection in Nodejs ‘undici’ via host

## Summary
Severity: Medium
Advisory: GHSA-5r9g-qh6m-jxff
CVE: CVE-2023-23936
CWE: CWE-74, CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-16
Source: https://github.com/advisories/GHSA-5r9g-qh6m-jxff
Type: github-advisory

## Affected
- npm: `undici` — affected >=2.0.0 <5.19.1

## Details
### Impact

undici library does not protect `host` HTTP header from CRLF injection vulnerabilities.

### Patches

This issue was patched in Undici v5.19.1.

### Workarounds

Sanitize the `headers.host` string before passing to undici.

### References

Reported at https://hackerone.com/reports/1820955.

### Credits

Thank you to Zhipeng Zhang ([@timon8](https://hackerone.com/timon8)) for reporting this vulnerability.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-5r9g-qh6m-jxff
- https://nvd.nist.gov/vuln/detail/CVE-2023-23936
- https://github.com/nodejs/undici/commit/a2eff05401358f6595138df963837c24348f2034
- https://hackerone.com/reports/1820955
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v5.19.1
