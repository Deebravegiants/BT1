# [H] Pion DTLS Header reconstruction method can be thrown into an infinite loop

## Summary
Severity: High
Advisory: GHSA-cm8f-h6j3-p25c
CVE: CVE-2022-29190
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cm8f-h6j3-p25c
Type: github-advisory

## Affected
- Go: `github.com/pion/dtls` — affected >=0 <2.1.4
- Go: `github.com/pion/dtls/v2` — affected >=0 <2.1.4

## Details
### Impact
An attacker can send packets that will send Pion DTLS into an infinite loop when processing.

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
- https://github.com/pion/dtls/security/advisories/GHSA-cm8f-h6j3-p25c
- https://nvd.nist.gov/vuln/detail/CVE-2022-29190
- https://github.com/pion/dtls/commit/e0b2ce3592e8e7d73713ac67b363a2e192a4cecf
- https://github.com/pion/dtls/releases/tag/v2.1.4
- https://pkg.go.dev/vuln/GO-2022-0460
- github.com/pion/dtls
