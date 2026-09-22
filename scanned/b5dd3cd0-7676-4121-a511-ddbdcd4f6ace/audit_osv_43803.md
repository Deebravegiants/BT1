# [M] Unbounded DAA Decompression in Pandora Allows Denial of Service via Decompression Bomb

## Summary
Severity: Medium
Advisory: CVE-2026-74767
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74767
Type: osv

## Details
Pandora contains a denial-of-service vulnerability in its handling of DAA (Direct Access Archive) files. When extracting the internal ISO image from a DAA archive, compressed chunks were decompressed using zlib.decompress() without enforcing a limit on the resulting uncompressed data.


An attacker able to submit a crafted DAA file containing highly compressed data could cause Pandora to decompress a relatively small input into a very large amount of data in memory. Because the decompressed chunks are accumulated to construct the internal ISO image, this could result in excessive memory consumption and potentially CPU exhaustion, causing the extraction worker to become unresponsive, terminate, or affect the availability of the Pandora service.


The patch introduces bounded decompression using decompressobj().decompress() with max_extracted_filesize, verifies the cumulative size of decompressed chunks, and raises a dedicated ZipBomb exception when the configured limit is exceeded. Pandora then aborts extraction and reports the file as too large.

## References
- https://github.com/pandora-analysis/pandora/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74767.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74767
- https://github.com/pandora-analysis/pandora/commit/f4294a873f86fbf2569c289e329fff2f52ca50c9
