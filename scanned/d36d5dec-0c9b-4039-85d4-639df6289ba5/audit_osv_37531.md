# [C] FreeRDP has a Heap Buffer Overflow in nsc_process_message() via Unchecked SURFACE_BITS_COMMAND Bitmap Dimensions

## Summary
Severity: Critical
Advisory: CVE-2026-31806
Aliases: GHSA-rrqm-46rj-cmx2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-31806
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.24.0,  the gdi_surface_bits() function processes SURFACE_BITS_COMMAND messages sent by the RDP server. When the command is handled using NSCodec, the bmp.width and bmp.height values provided by the server are not properly validated against the actual desktop dimensions. A malicious RDP server can supply crafted bmp.width and bmp.height values that exceed the expected surface size. Because these values are used during bitmap decoding and memory operations without proper bounds checking, this can lead to a heap buffer overflow. Since the attacker can also control the associated pixel data transmitted by the server, the overflow may be exploitable to overwrite adjacent heap memory. This vulnerability is fixed in 3.24.0.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31806.json
- https://access.redhat.com/errata/RHSA-2026:10076
- https://access.redhat.com/errata/RHSA-2026:10734
- https://access.redhat.com/errata/RHSA-2026:10735
- https://access.redhat.com/errata/RHSA-2026:10951
- https://access.redhat.com/errata/RHSA-2026:11323
- https://access.redhat.com/errata/RHSA-2026:19033
- https://access.redhat.com/errata/RHSA-2026:6340
- https://access.redhat.com/errata/RHSA-2026:6727
- https://access.redhat.com/errata/RHSA-2026:6743
- https://access.redhat.com/errata/RHSA-2026:6799
- https://access.redhat.com/errata/RHSA-2026:6918
- https://access.redhat.com/errata/RHSA-2026:6958
- https://access.redhat.com/errata/RHSA-2026:9640
- https://access.redhat.com/errata/RHSA-2026:9641
- https://access.redhat.com/security/cve/CVE-2026-31806
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31806.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-rrqm-46rj-cmx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-31806
- https://bugzilla.redhat.com/show_bug.cgi?id=2447376
