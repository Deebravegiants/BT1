# [H] GStreamer MXF File Parsing Use-After-Free Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-44446
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-44446
Type: osv

## Details
GStreamer MXF File Parsing Use-After-Free Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the parsing of MXF video files. The issue results from the lack of validating the existence of an object prior to performing operations on the object. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-22299.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00029.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44446.json
- https://gstreamer.freedesktop.org/security/sa-2023-0010.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-44446
- https://www.zerodayinitiative.com/advisories/ZDI-23-1647/
