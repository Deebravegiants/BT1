# [H] GStreamer H.266 Codec Parser Integer Underflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-3084
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-3084
Type: osv

## Details
GStreamer H.266 Codec Parser Integer Underflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the parsing of picture partitions. The issue results from the lack of proper validation of user-supplied data, which can result in an integer underflow before writing to memory. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28910.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-3084.json
- https://access.redhat.com/security/cve/CVE-2026-3084
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3084.json
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/commit/496e4f296e658fba7fd40027d3bbe6095633ec91
- https://nvd.nist.gov/vuln/detail/CVE-2026-3084
- https://www.zerodayinitiative.com/advisories/ZDI-26-169/
- https://bugzilla.redhat.com/show_bug.cgi?id=2447483
