# [H] Heap-buffer-overflow write in FFmpeg EXR dwa_uncompress

## Summary
Severity: High
Advisory: CVE-2025-59731
CVSS: 7.5 (CVSS:4.0/AV:A/AC:H/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2025-10-06
Source: https://osv.dev/vulnerability/CVE-2025-59731
Type: osv

## Details
When decoding an OpenEXR file that uses DWAA or DWAB compression, the specified raw length of run-length-encoded data is not checked when using it to calculate the output data.

We read rle_raw_size from the input file at [0], we decompress and decode into the buffer td->rle_raw_data of size rle_raw_size at [1], and then at [2] we will access entries in this buffer up to (td->xsize - 1) * (td->ysize - 1) + rle_raw_size / 2, which may exceed rle_raw_size.




We recommend upgrading to version 8.0 or beyond.

## References
- https://issuetracker.google.com/436510153
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59731.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59731
- https://git.ffmpeg.org/ffmpeg.git
