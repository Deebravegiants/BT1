# [M] ImageMagick has infinite loop when writing IPTCTEXT leads to denial of service via crafted profile

## Summary
Severity: Medium
Advisory: CVE-2026-26066
Aliases: GHSA-v994-63cg-9wj3
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2026-26066
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-15 and 6.9.13-40, a crafted profile contain invalid IPTC data may cause an infinite loop when writing it with `IPTCTEXT`. Versions 7.1.2-15 and 6.9.13-40 contain a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26066.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-v994-63cg-9wj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-26066
