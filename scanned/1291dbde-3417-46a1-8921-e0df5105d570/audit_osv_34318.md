# [H] Arbitrary Mattermost Team can be joined by manipulating the SAML RelayState

## Summary
Severity: High
Advisory: CVE-2025-58075
Aliases: GHSA-r6qj-894f-5hr2, GO-2025-4035
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-58075
Type: osv

## Details
Mattermost versions 10.11.x <= 10.11.1, 10.10.x <= 10.10.2, 10.5.x <= 10.5.10 fail to verify a user has permission to join a Mattermost team using the original invite token which allows any attacked to join any team on a Mattermost server regardless of restrictions via manipulating the RelayState

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58075.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-58075
