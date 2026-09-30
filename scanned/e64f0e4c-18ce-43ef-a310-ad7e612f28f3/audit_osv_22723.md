# [H] CVE-2022-36943

## Summary
Severity: High
Advisory: CVE-2022-36943
Aliases: GHSA-vgvw-6xcf-qqfc
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2023-01-03
Source: https://osv.dev/vulnerability/CVE-2022-36943
Type: osv

## Details
SSZipArchive versions 2.5.3 and older contain an arbitrary file write vulnerability due to lack of sanitization on paths which are symlinks. SSZipArchive will overwrite files on the filesystem when opening a malicious ZIP containing a symlink as the first item.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36943.json
- https://github.com/metaredteam/external-disclosures/security/advisories/GHSA-vgvw-6xcf-qqfc
- https://nvd.nist.gov/vuln/detail/CVE-2022-36943
