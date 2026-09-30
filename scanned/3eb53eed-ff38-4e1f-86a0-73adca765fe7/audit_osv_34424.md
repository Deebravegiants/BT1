# [H] Heap-buffer-overflow write in FFmpeg MDASH resolve_content_path

## Summary
Severity: High
Advisory: CVE-2025-59728
CVSS: 7.5 (CVSS:4.0/AV:A/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2025-10-06
Source: https://osv.dev/vulnerability/CVE-2025-59728
Type: osv

## Details
When calculating the content path in handling of MPEG-DASH manifests, there's an out-of-bounds NUL-byte write one byte past the end of the buffer.When we call xmlNodeGetContent below [0], it returns a buffer precisely allocated to match the string length, using strdup internally. If this buffer is not an empty string, it is assigned to root_url at [1].If the last (non-NUL) byte in this buffer is not '/' then we append '/' in-place at [2]. This will write two bytes into the buffer, starting at the last valid byte in the buffer, writing the NUL byte beyond the end of the allocated buffer.
We recommend upgrading to version 8.0 or beyond.

## References
- https://issuetracker.google.com/433502298
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59728.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59728
- https://git.ffmpeg.org/ffmpeg.git
