# [M] NoSQL Injection Leading to Authentication Bypass in your_spotify

## Summary
Severity: Medium
Advisory: CVE-2024-28192
Aliases: GHSA-c8wf-wcjc-2pvm
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-03-13
Source: https://osv.dev/vulnerability/CVE-2024-28192
Type: osv

## Details
your_spotify is an open source, self hosted Spotify tracking dashboard. YourSpotify version <1.8.0 is vulnerable to NoSQL injection in the public access token processing logic. Attackers can fully bypass the public token authentication mechanism, regardless if a public token has been generated before or not, without any user interaction or prerequisite knowledge. This vulnerability allows an attacker to fully bypass the public token authentication mechanism, regardless if a public token has been generated before or not, without any user interaction or prerequisite knowledge. This issue has been addressed in version 1.8.0. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28192.json
- https://github.com/Yooooomi/your_spotify/security/advisories/GHSA-c8wf-wcjc-2pvm
- https://nvd.nist.gov/vuln/detail/CVE-2024-28192
