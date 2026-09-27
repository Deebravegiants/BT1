# [H] Parse Server has Denial of Service (DoS) and Cloud Function Dispatch Bypass via Prototype Chain Resolution

## Summary
Severity: High
Advisory: GHSA-5j86-7r7m-p8h6
CVE: CVE-2026-30939
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-5j86-7r7m-p8h6
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <8.6.13
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.1-alpha.2

## Details
### Impact

An unauthenticated attacker can crash the Parse Server process by calling a Cloud Function endpoint with a prototype property name as the function name. The server recurses infinitely, causing a call stack size error that terminates the process.

Other prototype property names bypass Cloud Function dispatch validation and return HTTP 200 responses, even though no such Cloud Functions are defined. The same applies to dot-notation traversal.

All Parse Server deployments that expose the Cloud Function endpoint are affected.

### Patches

The internal handler registries for Cloud Functions, Jobs, Triggers, and Validators have been changed to prevent prototype chain properties from being resolved.

### Workarounds

Place a reverse proxy or WAF in front of Parse Server and block requests to `Object.prototype` property names.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-5j86-7r7m-p8h6
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.1-alpha.2
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.13

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-5j86-7r7m-p8h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-30939
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.13
- https://github.com/parse-community/parse-server/releases/tag/9.5.1-alpha.2
