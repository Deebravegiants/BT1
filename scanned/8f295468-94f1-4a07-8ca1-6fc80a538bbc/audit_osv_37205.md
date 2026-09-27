# [H] GStreamer RIFF Palette Integer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-2921
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-2921
Type: osv

## Details
GStreamer RIFF Palette Integer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GStreamer. Interaction with this library is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the handling of palette data in AVI files. The issue results from the lack of proper validation of user-supplied data, which can result in an integer overflow before writing to memory. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28854.

## References
- https://lists.debian.org/debian-lts-announce/2026/03/msg00018.html
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-2921.json
- https://access.redhat.com/errata/RHSA-2026:19024
- https://access.redhat.com/errata/RHSA-2026:19180
- https://access.redhat.com/errata/RHSA-2026:6259
- https://access.redhat.com/errata/RHSA-2026:6300
- https://access.redhat.com/errata/RHSA-2026:6750
- https://access.redhat.com/errata/RHSA-2026:7673
- https://access.redhat.com/errata/RHSA-2026:7850
- https://access.redhat.com/errata/RHSA-2026:8854
- https://access.redhat.com/errata/RHSA-2026:8857
- https://access.redhat.com/errata/RHSA-2026:8862
- https://access.redhat.com/errata/RHSA-2026:8874
- https://access.redhat.com/errata/RHSA-2026:8876
- https://access.redhat.com/errata/RHSA-2026:9446
- https://access.redhat.com/errata/RHSA-2026:9447
- https://access.redhat.com/errata/RHSA-2026:9487
- https://access.redhat.com/errata/RHSA-2026:9488
- https://access.redhat.com/security/cve/CVE-2026-2921
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2921.json
