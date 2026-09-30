# [H] Pi-hole Blind Server-Side Request Forgery (SSRF) vulnerability can lead to Remote Code Execution (RCE)

## Summary
Severity: High
Advisory: CVE-2024-34361
Aliases: GHSA-jg6g-rrj6-xfg6
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-34361
Type: osv

## Details
Pi-hole is a DNS sinkhole that protects devices from unwanted content without installing any client-side software. A vulnerability in versions prior to 5.18.3 allows an authenticated user to make internal requests to the server via the `gravity_DownloadBlocklistFromUrl()` function. Depending on some circumstances, the vulnerability could lead to remote command execution. Version 5.18.3 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34361.json
- https://github.com/pi-hole/pi-hole/security/advisories/GHSA-jg6g-rrj6-xfg6
- https://nvd.nist.gov/vuln/detail/CVE-2024-34361
- https://github.com/pi-hole/pi-hole/commit/2c497a9a3ea099079bbcd1eb21725b0ed54b529d
