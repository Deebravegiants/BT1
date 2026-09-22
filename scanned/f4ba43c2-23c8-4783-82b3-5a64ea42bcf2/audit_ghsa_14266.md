# [H] Hidden fields can be leaked on readable collections in Payload

## Summary
Severity: High
Advisory: GHSA-35jj-vqcf-f2jf
CVE: CVE-2023-30843
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-35jj-vqcf-f2jf
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <1.7.0

## Details
### Details

If a user has access to documents that contain hidden fields or fields they do not have access to, the user could reverse-engineer those values via brute force.

Affected versions:  < 1.7.0

### Workarounds

If you are unable to update, you can write a `beforeOperation` hook to remove `where` queries that attempt to access hidden field data.

### Detecting Compromise

Monitor your instance for brute-force style requests against your instance using `where` queries.

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-35jj-vqcf-f2jf
- https://nvd.nist.gov/vuln/detail/CVE-2023-30843
- https://github.com/payloadcms/payload
- https://github.com/payloadcms/payload/releases/tag/v1.7.0
