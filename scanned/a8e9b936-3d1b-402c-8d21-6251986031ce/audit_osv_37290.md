# [H] GStreamer H.266 Codec Parser Out-Of-Bounds Write Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-3086
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-3086
Type: osv

## Details
GStreamer H.266 Codec Parser Out-Of-Bounds Write Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the processing of APS units. The issue results from the lack of proper validation of user-supplied data, which can result in a write past the end of an allocated buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28911.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-3086.json
- https://access.redhat.com/security/cve/CVE-2026-3086
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3086.json
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/commit/025d59cf3459c2903f0384b6b94bc3235e177b53
- https://nvd.nist.gov/vuln/detail/CVE-2026-3086
- https://www.zerodayinitiative.com/advisories/ZDI-26-170/
- https://bugzilla.redhat.com/show_bug.cgi?id=2447493
