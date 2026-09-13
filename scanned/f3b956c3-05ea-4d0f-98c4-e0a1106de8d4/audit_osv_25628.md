# [H] GStreamer H265 Parsing Stack-based Buffer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-40476
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-40476
Type: osv

## Details
GStreamer H265 Parsing Stack-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the parsing of H265 encoded video files. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length stack-based buffer. An attacker can leverage this vulnerability to execute code in the context of the current process.
. Was ZDI-CAN-21768.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00038.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40476.json
- https://gstreamer.freedesktop.org/security/sa-2023-0008.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-40476
- https://www.zerodayinitiative.com/advisories/ZDI-23-1458/
