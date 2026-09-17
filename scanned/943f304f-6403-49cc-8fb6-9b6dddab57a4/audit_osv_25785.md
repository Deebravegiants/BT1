# [H] Out-of-bounds write in exiv2

## Summary
Severity: High
Advisory: CVE-2023-44398
Aliases: GHSA-hrw9-ggg3-3r4r, PYSEC-2023-233
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/CVE-2023-44398
Type: osv

## Details
Exiv2 is a C++ library and a command-line utility to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata. An out-of-bounds write was found in Exiv2 version v0.28.0. The vulnerable function, `BmffImage::brotliUncompress`, is new in v0.28.0, so earlier versions of Exiv2 are _not_ affected. The out-of-bounds write is triggered when Exiv2 is used to read the metadata of a crafted image file. An attacker could potentially exploit the vulnerability to gain code execution, if they can trick the victim into running Exiv2 on a crafted image file. This bug is fixed in version v0.28.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44398.json
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-hrw9-ggg3-3r4r
- https://nvd.nist.gov/vuln/detail/CVE-2023-44398
- https://security.gentoo.org/glsa/202312-06
- https://github.com/Exiv2/exiv2/commit/e884a0955359107f4031c74a07406df7e99929a5
