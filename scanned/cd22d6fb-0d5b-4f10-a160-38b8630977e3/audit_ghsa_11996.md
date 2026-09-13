# [H] parse-server's endpoint `/loginAs` allows `readOnlyMasterKey` to gain full read and write access as any user

## Summary
Severity: High
Advisory: GHSA-79wj-8rqv-jvp5
CVE: CVE-2026-30229
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-79wj-8rqv-jvp5
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <8.6.6
- npm: `parse-server` — affected >=9.0.0 <9.5.0-alpha.4

## Details
### Impact

The `readOnlyMasterKey` can call `POST /loginAs` to obtain a valid session token for any user. This allows a read-only credential to impersonate arbitrary users with full read and write access to their data. Any Parse Server deployment that uses `readOnlyMasterKey` is affected.

### Patches

The fix adds a check to the `/logInAs` handler.

### Workarounds

There is no workaround other than not using `readOnlyMasterKey`.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-79wj-8rqv-jvp5
- Fix for Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.4
- Fix for Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.6

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-79wj-8rqv-jvp5
- https://nvd.nist.gov/vuln/detail/CVE-2026-30229
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.6
- https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.4
