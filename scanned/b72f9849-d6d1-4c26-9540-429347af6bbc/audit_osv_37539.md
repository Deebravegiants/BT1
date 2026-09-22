# [M] ImageMagick has a heap buffer over-write on 32-bit systems in SFW decoder

## Summary
Severity: Medium
Advisory: CVE-2026-31853
Aliases: GHSA-56jp-jfqg-f8f4
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31853
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to 7.1.2-16 and 6.9.13-41, an overflow on 32-bit systems can cause a crash in the SFW decoder when processing extremely large images. This vulnerability is fixed in 7.1.2-16 and 6.9.13-41.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31853.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-56jp-jfqg-f8f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-31853
