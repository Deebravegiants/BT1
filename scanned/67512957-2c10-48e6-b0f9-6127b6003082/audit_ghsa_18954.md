# [H] Parse Server Vulnerable to Server-Side Request Forgery (SSRF) in File Upload via URI Format

## Summary
Severity: High
Advisory: GHSA-x4qj-2f4q-r4rx
CVE: CVE-2025-64430
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-05
Source: https://github.com/advisories/GHSA-x4qj-2f4q-r4rx
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=4.2.0 <7.5.4
- npm: `parse-server` — affected >=8.0.0 <8.4.0-alpha.2

## Details
### Impact

A Server-Side Request Forgery (SSRF) vulnerability in the file upload functionality when trying to upload a `Parse.File` with `uri` parameter allows to execute an arbitrary URI. The vulnerability stems from a file upload feature in which Parse Server retrieves the file data from a URI that is provided in the request. A request to the provided URI is executed, but the response is not stored in Parse Server's file storage as the server crashes upon receiving the response.

### Patches

The feature has been implemented in Parse Server 4.2.0 but never worked and reliably crashes the server when trying to use it due to a bug in its implementation. Since the feature is not currently working, and due to its risky nature, it has been removed to address the vulnerability.

### Workarounds

None.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-x4qj-2f4q-r4rx
- https://nvd.nist.gov/vuln/detail/CVE-2025-64430
- https://github.com/parse-community/parse-server/pull/9903
- https://github.com/parse-community/parse-server/pull/9904
- https://github.com/parse-community/parse-server/commit/8bbe3efbcf4a3b66f4a8db9bfb18cd98c050db51
- https://github.com/parse-community/parse-server/commit/97763863b72689a29ad7a311dfb590c3e3c50585
- https://github.com/parse-community/parse-server
