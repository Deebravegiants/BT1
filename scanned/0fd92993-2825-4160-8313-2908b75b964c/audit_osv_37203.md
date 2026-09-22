# [H] GStreamer ASF Demuxer Heap-based Buffer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-2920
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-2920
Type: osv

## Details
GStreamer ASF Demuxer Heap-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the processing of stream headers within ASF files. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length heap-based buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28843.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-2920.json
- https://access.redhat.com/errata/RHSA-2026:19024
- https://access.redhat.com/errata/RHSA-2026:19180
- https://access.redhat.com/errata/RHSA-2026:6259
- https://access.redhat.com/errata/RHSA-2026:6300
- https://access.redhat.com/errata/RHSA-2026:6750
- https://access.redhat.com/errata/RHSA-2026:8854
- https://access.redhat.com/errata/RHSA-2026:8862
- https://access.redhat.com/security/cve/CVE-2026-2920
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2920.json
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/commit/37d7991168a223d0810fd1f4493ec6a8b6a510d3
- https://nvd.nist.gov/vuln/detail/CVE-2026-2920
- https://www.zerodayinitiative.com/advisories/ZDI-26-164/
- https://bugzilla.redhat.com/show_bug.cgi?id=2447490
