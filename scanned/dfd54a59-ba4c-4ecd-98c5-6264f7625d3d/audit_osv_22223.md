# [H] OS command injection in iTunesRPC-Remastered

## Summary
Severity: High
Advisory: CVE-2022-23611
Aliases: GHSA-mjv7-r62p-vhhg
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:H)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2022-23611
Type: osv

## Details
iTunesRPC-Remastered is a Discord Rich Presence for iTunes on Windows utility. In affected versions iTunesRPC-Remastered did not properly sanitize image file paths leading to OS level command injection. This issue has been patched in commit cdcd48b. Users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23611.json
- https://github.com/bildsben/iTunesRPC-Remastered/security/advisories/GHSA-mjv7-r62p-vhhg
- https://nvd.nist.gov/vuln/detail/CVE-2022-23611
- https://github.com/bildsben/iTunesRPC-Remastered/commit/cdcd48bbc44009ddcbd07a809b87376dc9ce37f4
