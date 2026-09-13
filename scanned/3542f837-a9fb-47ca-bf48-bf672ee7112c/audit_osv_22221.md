# [H] Path traveresal in iTunesRPC-Remastered

## Summary
Severity: High
Advisory: CVE-2022-23609
Aliases: GHSA-cc8j-fr7v-7r6q
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2022-23609
Type: osv

## Details
iTunesRPC-Remastered is a Discord Rich Presence for iTunes on Windows utility. In affected versions iTunesRPC-Remastered did not properly sanitize user input used to remove files leading to file deletion only limited by the process permissions. Users are advised to upgrade as soon as possible.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23609.json
- https://github.com/bildsben/iTunesRPC-Remastered/security/advisories/GHSA-cc8j-fr7v-7r6q
- https://nvd.nist.gov/vuln/detail/CVE-2022-23609
- https://github.com/bildsben/iTunesRPC-Remastered/commit/1eb1e5428f0926b2829a0bbbb65b0d946e608593
