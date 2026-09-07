# [H] tiny-csrf has openly visible CSRF tokens

## Summary
Severity: High
Advisory: GHSA-pj2c-h76w-vv6f
CVE: CVE-2022-39287
CWE: CWE-319
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-pj2c-h76w-vv6f
Type: github-advisory

## Affected
- npm: `tiny-csrf` — affected >=0 <1.1.0

## Details
### Impact

Weak encryption on CSRF so tokens can be read by malicious attackers. 

### Patches

Problems have been patched as of v1.1.0

### Workarounds

Upgrade to v1.1.0

### References

https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html 

### For more information

Submit an issue at [the github repo](https://github.com/valexandersaulys/tiny-csrf)

## References
- https://github.com/valexandersaulys/tiny-csrf/security/advisories/GHSA-pj2c-h76w-vv6f
- https://nvd.nist.gov/vuln/detail/CVE-2022-39287
- https://github.com/valexandersaulys/tiny-csrf/commit/8eead6da3b56e290512bbe8d20c2c5df3be317ba
- https://github.com/valexandersaulys/tiny-csrf
