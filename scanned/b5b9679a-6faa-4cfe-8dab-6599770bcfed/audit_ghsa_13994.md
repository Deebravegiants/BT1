# [M] Invalid push request payload crashes Parse Server

## Summary
Severity: Medium
Advisory: GHSA-mxhg-rvwx-x993
CVE: CVE-2023-32688
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-mxhg-rvwx-x993
Type: github-advisory

## Affected
- npm: `parse-server-push-adapter` — affected >=0 <4.1.3

## Details
### Impact

The Parse Server Push Adapter can crash Parse Server due to an invalid push notification payload.

### Patches

Invalid push notification payload is caught and an logged.

### Workarounds
n/a

### References
- https://github.com/parse-community/parse-server-push-adapter/security/advisories/GHSA-mxhg-rvwx-x993
- https://github.com/parse-community/parse-server-push-adapter/pull/217

## References
- https://github.com/parse-community/parse-server-push-adapter/security/advisories/GHSA-mxhg-rvwx-x993
- https://nvd.nist.gov/vuln/detail/CVE-2023-32688
- https://github.com/parse-community/parse-server-push-adapter/pull/217
- https://github.com/parse-community/parse-server-push-adapter/commit/598cb84d0866b7c5850ca96af920e8cb5ba243ec
- https://github.com/parse-community/parse-server-push-adapter
- https://github.com/parse-community/parse-server-push-adapter/releases/tag/4.1.3
