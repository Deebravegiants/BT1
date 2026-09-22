# [H] GStreamer FLAC File Parsing Integer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-37327
CVSS: 7.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-37327
Type: osv

## Details
GStreamer FLAC File Parsing Integer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the parsing of FLAC audio files. The issue results from the lack of proper validation of user-supplied data, which can result in an integer overflow before allocating a buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-20775.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IGQEFZ6ZB3C2XU4JQD3IAFMQIN456W2D/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37327.json
- https://gstreamer.freedesktop.org/security/sa-2023-0001.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-37327
- https://www.zerodayinitiative.com/advisories/ZDI-23-903/
