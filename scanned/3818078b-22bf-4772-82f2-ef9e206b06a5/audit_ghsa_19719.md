# [H] Vela Server Has Insufficient Webhook Payload Data Verification

## Summary
Severity: High
Advisory: GHSA-9m63-33q3-xq5x
CVE: CVE-2025-27616
CWE: CWE-290, CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-9m63-33q3-xq5x
Type: github-advisory

## Affected
- Go: `github.com/go-vela/server` — affected >=0 <0.25.3
- Go: `github.com/go-vela/server` — affected >=0.26.0 <0.26.3

## Details
### Impact
Users with an enabled repository with access to repo level CI secrets in Vela are vulnerable to the exploit. 

Any user with access to the CI instance and the linked source control manager can perform the exploit.

### Method
By spoofing a webhook payload with a specific set of headers and body data, an attacker could transfer ownership of a repository and its repo level secrets to a separate repository. 

These secrets could be exfiltrated by follow up builds to the repository.

### Patches
`v0.26.3` — Image: `target/vela-server:v0.26.3`
`v0.25.3` — Image: `target/vela-server:v0.25.3`

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

There are no workarounds to the issue.

### References
_Are there any links users can visit to find out more?_

Please see linked CWEs (common weakness enumerators) for more information.

## References
- https://github.com/go-vela/server/security/advisories/GHSA-9m63-33q3-xq5x
- https://nvd.nist.gov/vuln/detail/CVE-2025-27616
- https://github.com/go-vela/server/commit/257886e5a3eea518548387885894e239668584f5
- https://github.com/go-vela/server/commit/67c1892e2464dc54b8d2588815dfb7819222500b
- https://github.com/go-vela/server
- https://github.com/go-vela/server/releases/tag/v0.25.3
- https://github.com/go-vela/server/releases/tag/v0.26.3
- https://pkg.go.dev/vuln/GO-2025-3509
