# [M] CVE-2022-44267

## Summary
Severity: Medium
Advisory: CVE-2022-44267
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-02-06
Source: https://osv.dev/vulnerability/CVE-2022-44267
Type: osv

## Details
ImageMagick 7.1.0-49 is vulnerable to Denial of Service. When it parses a PNG image (e.g., for resize), the convert process could be left waiting for stdin input.

## References
- https://imagemagick.org/
- https://www.metabaseq.com/imagemagick-zero-days/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44267.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AINSUL2QBKETGYRPA7XSCMJWLUB44M6S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZZLLS37P67CMBRML6OCG42GPCKGRCJNV/
- https://nvd.nist.gov/vuln/detail/CVE-2022-44267
- https://www.debian.org/security/2023/dsa-5347
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
