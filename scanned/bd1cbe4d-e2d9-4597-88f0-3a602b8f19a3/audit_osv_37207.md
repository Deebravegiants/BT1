# [H] GStreamer DVB Subtitles Out-Of-Bounds Write Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-2923
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-2923
Type: osv

## Details
GStreamer DVB Subtitles Out-Of-Bounds Write Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the handling of coordinates. The issue results from the lack of proper validation of user-supplied data, which can result in a write past the end of an allocated buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28838.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-2923.json
- https://access.redhat.com/errata/RHSA-2026:19024
- https://access.redhat.com/errata/RHSA-2026:19180
- https://access.redhat.com/errata/RHSA-2026:6259
- https://access.redhat.com/errata/RHSA-2026:6300
- https://access.redhat.com/errata/RHSA-2026:6750
- https://access.redhat.com/errata/RHSA-2026:8854
- https://access.redhat.com/errata/RHSA-2026:8862
- https://access.redhat.com/security/cve/CVE-2026-2923
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2923.json
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/commit/3b8253f447bcc9831dbf643d2c69b205fedbe086
- https://nvd.nist.gov/vuln/detail/CVE-2026-2923
- https://www.zerodayinitiative.com/advisories/ZDI-26-161/
- https://bugzilla.redhat.com/show_bug.cgi?id=2447503
