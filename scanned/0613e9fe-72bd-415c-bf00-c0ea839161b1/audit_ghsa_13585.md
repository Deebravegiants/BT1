# [H] Parse Server may crash when uploading file without extension

## Summary
Severity: High
Advisory: GHSA-792q-q67h-w579
CVE: CVE-2023-46119
CWE: CWE-22, CWE-23
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-24
Source: https://github.com/advisories/GHSA-792q-q67h-w579
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=1.0.0 <5.5.6
- npm: `parse-server` — affected >=6.0.0 <6.3.1

## Details
### Impact

Parse Server crashes when uploading a file without extension.

### Patches

A permanent fix has been implemented to prevent the server from crashing.

### Workarounds

There are no known workarounds.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-792q-q67h-w579
- Patched in Parse Server 6: https://github.com/parse-community/parse-server/releases/tag/6.3.1
- Patched in Parse Server 5 (LTS): https://github.com/parse-community/parse-server/releases/tag/5.5.6

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-792q-q67h-w579
- https://nvd.nist.gov/vuln/detail/CVE-2023-46119
- https://github.com/parse-community/parse-server/commit/686a9f282dc23c31beab3d93e6d21ccd0e1328fe
- https://github.com/parse-community/parse-server/commit/fd86278919556d3682e7e2c856dfccd5beffbfc0
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/5.5.6
- https://github.com/parse-community/parse-server/releases/tag/6.3.1
