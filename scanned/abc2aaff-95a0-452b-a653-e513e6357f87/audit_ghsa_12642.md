# [C] Parse Server vulnerable to remote code execution via MongoDB BSON parser through prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-462x-c3jw-7vr6
CVE: CVE-2023-36475
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-462x-c3jw-7vr6
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <5.5.2
- npm: `parse-server` — affected >=6.0.0 <6.2.1

## Details
### Impact

An attacker can use this prototype pollution sink to trigger a remote code execution through the MongoDB BSON parser.

### Patches

Prevent prototype pollution in MongoDB database adapter.

### Workarounds

Disable remote code execution through the MongoDB BSON parser.

### Credits

- Discovered by hir0ot working with Trend Micro Zero Day Initiative
- Fixed by dbythy
- Reviewed by mtrezza

### References

- https://github.com/parse-community/parse-server/security/advisories/GHSA-462x-c3jw-7vr6
- https://github.com/advisories/GHSA-prm5-8g2m-24gg

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-462x-c3jw-7vr6
- https://nvd.nist.gov/vuln/detail/CVE-2023-36475
- https://github.com/parse-community/parse-server/issues/8674
- https://github.com/parse-community/parse-server/issues/8675
- https://github.com/parse-community/parse-server/commit/3dd99dd80e27e5e1d99b42844180546d90c7aa90
- https://github.com/parse-community/parse-server/commit/5fad2928fb8ee17304abcdcf259932f827d8c81f
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/5.5.2
- https://github.com/parse-community/parse-server/releases/tag/6.2.1
