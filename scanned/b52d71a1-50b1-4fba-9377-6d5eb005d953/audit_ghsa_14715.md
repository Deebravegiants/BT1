# [H] path-to-regexp contains a ReDoS

## Summary
Severity: High
Advisory: GHSA-rhx6-c78j-4q9w
CVE: CVE-2024-52798
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-05
Source: https://github.com/advisories/GHSA-rhx6-c78j-4q9w
Type: github-advisory

## Affected
- npm: `path-to-regexp` — affected >=0 <0.1.12

## Details
### Impact

The regular expression that is vulnerable to backtracking can be generated in versions before 0.1.12 of `path-to-regexp`, originally reported in CVE-2024-45296

### Patches

Upgrade to 0.1.12.

### Workarounds

Avoid using two parameters within a single path segment, when the separator is not `.` (e.g. no `/:a-:b`). Alternatively, you can define the regex used for both parameters and ensure they do not overlap to allow backtracking.

### References

- https://github.com/advisories/GHSA-9wv6-86v2-598j
- https://blakeembrey.com/posts/2024-09-web-redos/

## References
- https://github.com/pillarjs/path-to-regexp/security/advisories/GHSA-rhx6-c78j-4q9w
- https://nvd.nist.gov/vuln/detail/CVE-2024-52798
- https://github.com/pillarjs/path-to-regexp/commit/f01c26a013b1889f0c217c643964513acf17f6a4
- https://blakeembrey.com/posts/2024-09-web-redos
- https://github.com/pillarjs/path-to-regexp
- https://security.netapp.com/advisory/ntap-20250124-0002
