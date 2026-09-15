# [H] GStreamer MRF File Parsing Out-Of-Bounds Write Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-18295
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-18295
Type: osv

## Details
GStreamer MRF File Parsing Out-Of-Bounds Write Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of MRF files. The issue results from the lack of proper validation of user-supplied data, which can result in a write past the end of an allocated buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-29510.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18295.json
- https://gstreamer.freedesktop.org/security/sa-2026-0050.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-18295
- https://www.zerodayinitiative.com/advisories/ZDI-26-463/
