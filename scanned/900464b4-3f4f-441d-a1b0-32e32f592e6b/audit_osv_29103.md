# [M] Exiv2 has an out-of-bounds read in AsfVideo::streamProperties

## Summary
Severity: Medium
Advisory: CVE-2024-39695
Aliases: GHSA-38rv-8x93-pvrh
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/CVE-2024-39695
Type: osv

## Details
Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. An out-of-bounds read was found in Exiv2 version v0.28.2. The vulnerability is in the parser for the ASF video format, which was a new feature in v0.28.0. The out-of-bounds read is triggered when Exiv2 is used to read the metadata of a crafted video file. The bug is fixed in version v0.28.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39695.json
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-38rv-8x93-pvrh
- https://nvd.nist.gov/vuln/detail/CVE-2024-39695
- https://github.com/Exiv2/exiv2/commit/3a28346db5ae1735a8728fe3491b0aecc1dbf387
- https://github.com/Exiv2/exiv2/pull/3006
