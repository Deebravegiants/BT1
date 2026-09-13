# [M] Unchecked hostname resolution could allow access to local network resources by users outside the local network

## Summary
Severity: Medium
Advisory: GHSA-6rg3-8h8x-5xfv
CWE: CWE-284, CWE-441
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-6rg3-8h8x-5xfv
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=1.2.0 <1.2.1

## Details
### Impact
A newly implemented route allowing users to download files from remote endpoints was not properly verifying the destination hostname for user provided URLs. This would allow malicious users to potentially access resources on local networks that would otherwise be inaccessible.

This vulnerability requires valid authentication credentials and is therefore **not exploitable by unauthenticated users**. If you are running an instance for yourself or other trusted individuals this impact is unlikely to be of major concern to you. However, you should still upgrade for security sake.

### Patches
Users should upgrade to the latest version of Wings.

### Workarounds
There is no workaround available that does not involve modifying Panel or Wings code.

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-6rg3-8h8x-5xfv
- https://github.com/pterodactyl/wings
