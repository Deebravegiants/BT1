# [M] CVE-2022-44268

## Summary
Severity: Medium
Advisory: CVE-2022-44268
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-02-06
Source: https://osv.dev/vulnerability/CVE-2022-44268
Type: osv

## Details
ImageMagick 7.1.0-49 is vulnerable to Information Disclosure. When it parses a PNG image (e.g., for resize), the resulting image could have embedded the content of an arbitrary. file (if the magick binary has permissions to read it).

## References
- http://packetstormsecurity.com/files/171727/ImageMagick-7.1.0-48-Arbitrary-File-Read.html
- https://imagemagick.org/
- https://www.metabaseq.com/imagemagick-zero-days/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44268.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AINSUL2QBKETGYRPA7XSCMJWLUB44M6S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZZLLS37P67CMBRML6OCG42GPCKGRCJNV/
- https://nvd.nist.gov/vuln/detail/CVE-2022-44268
- https://www.debian.org/security/2023/dsa-5347
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
