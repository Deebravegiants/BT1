# [M] Matthias-Wandel jhead exif.c PrintFormatNumber heap-based overflow

## Summary
Severity: Medium
Advisory: CVE-2024-2824
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-03-22
Source: https://osv.dev/vulnerability/CVE-2024-2824
Type: osv

## Details
A vulnerability was found in Matthias-Wandel jhead 3.08 and classified as critical. This issue affects the function PrintFormatNumber of the file exif.c. The manipulation leads to heap-based buffer overflow. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-257711.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2824.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2824
- https://vuldb.com/?id.257711
- https://github.com/Matthias-Wandel/jhead/issues/84
- https://vuldb.com/?ctiid.257711
- https://github.com/Matthias-Wandel/jhead/files/14613084/poc.zip
