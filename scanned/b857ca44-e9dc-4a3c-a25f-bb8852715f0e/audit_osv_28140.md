# [M] Disclosure of Spotify API Access Tokens to Guest Users Using Public Tokens in your_spotify

## Summary
Severity: Medium
Advisory: CVE-2024-28193
Aliases: GHSA-3782-758f-mj85
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-13
Source: https://osv.dev/vulnerability/CVE-2024-28193
Type: osv

## Details
your_spotify is an open source, self hosted Spotify tracking dashboard. YourSpotify version <1.8.0 allows users to create a public token in the settings, which can be used to provide guest-level access to the information of that specific user in YourSpotify. The /me API endpoint discloses Spotify API access and refresh tokens to guest users. Attackers with access to a public token for guest access to YourSpotify can therefore obtain access to Spotify API tokens of YourSpotify users. As a consequence, attackers may extract profile information, information about listening habits, playlists and other information from the corresponding Spotify profile. In addition, the attacker can pause and resume playback in the Spotify app at will. This issue has been resolved in version 1.8.0. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28193.json
- https://github.com/Yooooomi/your_spotify/security/advisories/GHSA-3782-758f-mj85
- https://nvd.nist.gov/vuln/detail/CVE-2024-28193
