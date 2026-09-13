# [H] GStreamer H.266 Codec Parser Stack-based Buffer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-3081
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-3081
Type: osv

## Details
GStreamer H.266 Codec Parser Stack-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the parsing of decoding units. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length stack-based buffer. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28839.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-3081.json
- https://access.redhat.com/security/cve/CVE-2026-3081
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3081.json
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/commit/2ffdfca2df95a7f605c922d3111e5d5be5314dca
- https://nvd.nist.gov/vuln/detail/CVE-2026-3081
- https://www.zerodayinitiative.com/advisories/ZDI-26-162/
- https://bugzilla.redhat.com/show_bug.cgi?id=2447494
