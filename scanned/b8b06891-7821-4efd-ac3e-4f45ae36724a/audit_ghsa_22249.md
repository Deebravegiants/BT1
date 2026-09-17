# [M] Pion/DTLS contains buffer for inbound DTLS fragments with no limit

## Summary
Severity: Medium
Advisory: GHSA-cx94-mrg9-rq4j
CVE: CVE-2022-29189
CWE: CWE-120
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cx94-mrg9-rq4j
Type: github-advisory

## Affected
- Go: `github.com/pion/dtls` — affected >=0 <2.1.4
- Go: `github.com/pion/dtls/v2` — affected >=0 <2.1.4

## Details
### Impact
A buffer that was used for inbound network traffic had no upper limit. Pion DTLS would buffer all network traffic from the remote user until the handshake completes or times out. An attacker could exploit this to cause excessive memory usage.

### Patches
Upgrade to Pion DTLS v2.1.4

### Workarounds
No workarounds available, upgrade to Pion DTLS v2.1.4

### References
Thank you to [Juho Nurminen](https://github.com/jupenur) and the Mattermost team for discovering and reporting this. 

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Pion DTLS](http://github.com/pion/dtls)
* Email us at [team@pion.ly](mailto:team@pion.ly)

## References
- https://github.com/pion/dtls/security/advisories/GHSA-cx94-mrg9-rq4j
- https://nvd.nist.gov/vuln/detail/CVE-2022-29189
- https://github.com/pion/dtls/commit/a6397ff7282bc56dc37a68ea9211702edb4de1de
- https://github.com/pion/dtls/releases/tag/v2.1.4
- https://pkg.go.dev/vuln/GO-2022-0461
- github.com/pion/dtls
