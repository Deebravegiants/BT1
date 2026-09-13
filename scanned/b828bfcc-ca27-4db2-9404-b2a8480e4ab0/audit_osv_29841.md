# [H] CVE-2024-46953

## Summary
Severity: High
Advisory: CVE-2024-46953
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-10
Source: https://osv.dev/vulnerability/CVE-2024-46953
Type: osv

## Details
An issue was discovered in base/gsdevice.c in Artifex Ghostscript before 10.04.0. An integer overflow when parsing the filename format string (for the output filename) results in path truncation, and possible path traversal and code execution.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=707793
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/ghostpdl.git/commit/?id=1f21a45df0fa3abec4cff12951022b192dda3c00
- https://github.com/ArtifexSoftware/ghostpdl/blob/master/doc/News.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00023.html
- https://www.suse.com/support/update/announcement/2024/suse-su-20243942-1/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46953.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46953
