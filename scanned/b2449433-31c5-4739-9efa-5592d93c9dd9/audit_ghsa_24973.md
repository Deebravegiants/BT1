# [M] Pion/DLTS Accepts Client Certificates Without CertificateVerify

## Summary
Severity: Medium
Advisory: GHSA-w45j-f832-hxvh
CVE: CVE-2022-29222
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-w45j-f832-hxvh
Type: github-advisory

## Affected
- Go: `github.com/pion/dtls` — affected >=0 <2.1.5
- Go: `github.com/pion/dtls/v2` — affected >=0 <2.1.5

## Details
### Impact
A DTLS Client could provide a Certificate that it doesn't posses the private key for and Pion DTLS wouldn't reject it. 

This issue affects users that are using Client certificates only. The connection itself is still secure. The Certificate provided by clients can't be trusted when using a Pion DTLS server prior to v2.1.5

### Patches
Upgrade to Pion DTLS v2.1.5

### Workarounds
No workarounds available, upgrade to Pion DTLS v2.1.5

### References
Thank you to [Juho Nurminen](https://github.com/jupenur) and the Mattermost team for discovering and reporting this. 

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Pion DTLS](http://github.com/pion/dtls)
* Email us at [team@pion.ly](mailto:team@pion.ly)

## References
- https://github.com/pion/dtls/security/advisories/GHSA-w45j-f832-hxvh
- https://nvd.nist.gov/vuln/detail/CVE-2022-29222
- https://github.com/pion/dtls/commit/d2f797183a9f044ce976e6df6f362662ca722412
- https://github.com/pion/dtls/releases/tag/v2.1.5
- https://pkg.go.dev/vuln/GO-2022-0462
- github.com/pion/dtls
