# [M] Navidrome Parameter Tampering vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4jrx-5w4h-3gpm
CVE: CVE-2024-32963
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-01
Source: https://github.com/advisories/GHSA-4jrx-5w4h-3gpm
Type: github-advisory

## Affected
- Go: `github.com/navidrome/navidrome` — affected >=0 <0.52.0

## Details
### Summary
Parameter tampering is a vulnerability where an attacker has the ability to manipulate parameter values in the HTTP requests.

### Details
The attacker is able to change the parameter values in the body and successfully impersonate another user. In this case, the attacker created a playlist, added song, posted arbitrary comment, set the playlist to be public, and put the admin as the owner of the playlist.

### Impact
Each known user is impacted. An attacker can obtain the ownerId from shared playlist information, meaning every user who has shared a playlist is also impacted, as they can be impersonated.

## References
- https://github.com/navidrome/navidrome/security/advisories/GHSA-4jrx-5w4h-3gpm
- https://nvd.nist.gov/vuln/detail/CVE-2024-32963
- https://github.com/navidrome/navidrome
