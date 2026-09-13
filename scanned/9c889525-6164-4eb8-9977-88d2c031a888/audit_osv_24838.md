# [H] CVE-2023-27534

## Summary
Severity: High
Advisory: CVE-2023-27534
Aliases: CURL-CVE-2023-27534
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-27534
Type: osv

## Details
A path traversal vulnerability exists in curl <8.0.0 SFTP implementation causes the tilde (~) character to be wrongly replaced when used as a prefix in the first path element, in addition to its intended use as the first element to indicate a path relative to the user's home directory. Attackers can exploit this flaw to bypass filtering or execute arbitrary code by crafting a path like /~2/foo while accessing a server with a specific user.

## References
- https://hackerone.com/reports/1892351
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27534.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/36NBD5YLJXXEDZLDGNFCERWRYJQ6LAQW/
- https://nvd.nist.gov/vuln/detail/CVE-2023-27534
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230420-0012/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00016.html
