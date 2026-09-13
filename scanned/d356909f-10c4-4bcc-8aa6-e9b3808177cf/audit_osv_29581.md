# [H] GStreamer EXIF Metadata Parsing Integer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2024-4453
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2024-4453
Type: osv

## Details
GStreamer EXIF Metadata Parsing Integer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the parsing of EXIF metadata. The issue results from the lack of proper validation of user-supplied data, which can result in an integer overflow before allocating a buffer. An attacker can leverage this vulnerability to execute code in the context of the current process.
. Was ZDI-CAN-23896.

## References
- https://lists.debian.org/debian-lts-announce/2024/05/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4453.json
- https://gitlab.freedesktop.org/tpm/gstreamer/-/commit/e68eccff103ab0e91e6d77a892f57131b33902f5
- https://nvd.nist.gov/vuln/detail/CVE-2024-4453
- https://www.zerodayinitiative.com/advisories/ZDI-24-467/
