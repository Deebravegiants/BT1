# [M] Heap-buffer-overflow read in FFmpeg DHAV get_duration

## Summary
Severity: Medium
Advisory: CVE-2025-59729
CVSS: 6.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:L/UI:P/VC:L/VI:H/VA:N/SC:L/SI:H/SA:N)
Published: 2025-10-06
Source: https://osv.dev/vulnerability/CVE-2025-59729
Type: osv

## Details
When parsing the header for a DHAV file, there's an integer underflow in offset calculation that leads to reading the duration from before the start of the allocated buffer.

If we load a DHAV file that is larger than MAX_DURATION_BUFFER_SIZE bytes (0x100000) for example 0x101000 bytes, then at [0] we have size = 0x101000. At [1] we have end_buffer_size = 0x100000, and at [2] we have end_buffer_pos = 0x1000.

The loop then scans backwards through the buffer looking for the dhav tag; when it is found, we'll calculate end_pos based on a 32-bit offset read from the buffer.

There is subsequently a check [3] that end_pos is within the section of the file that has been copied into end_buffer, but it only correctly handles the cases where end_pos is before the start of the file or after the section copied into end_buffer, and not the case where end_pos is within the the file, but before the section copied into end_buffer. If we provide such an offset, (end_pos - end_buffer_pos) can underflow, resulting in the subsequent access at [4] occurring before the beginning of the allocation.

We recommend upgrading to version 8.0 or beyond.

## References
- https://issuetracker.google.com/433513232
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59729.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59729
- https://git.ffmpeg.org/ffmpeg.git
