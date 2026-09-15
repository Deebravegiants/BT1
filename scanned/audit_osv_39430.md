# [C] Heap-buffer-overflow write in planar bitmap decoder

## Summary
Severity: Critical
Advisory: CVE-2026-45700
Aliases: GHSA-mpxh-8fq3-x8mh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45700
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.26.0, FreeRDP's planar bitmap decoder has an out-of-bounds heap write when decoding RLE planar data. In libfreerdp/codec/planar.c, freerdp_bitmap_decompress_planar() validates the X destination coordinate nXDst against the caller-provided destination stride (nDstStep) even when it is writing into the internal temp buffer pTempData. An attacker can bypass the check with a large nDstStep and a large nXDst, causing planar_decompress_plane_rle() to write past the end of pTempData. This vulnerability is fixed in 3.26.0.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45700.json
- https://access.redhat.com/errata/RHSA-2026:36203
- https://access.redhat.com/errata/RHSA-2026:37207
- https://access.redhat.com/errata/RHSA-2026:38501
- https://access.redhat.com/errata/RHSA-2026:46383
- https://access.redhat.com/errata/RHSA-2026:46384
- https://access.redhat.com/errata/RHSA-2026:46388
- https://access.redhat.com/errata/RHSA-2026:46389
- https://access.redhat.com/errata/RHSA-2026:46393
- https://access.redhat.com/errata/RHSA-2026:47048
- https://access.redhat.com/errata/RHSA-2026:47049
- https://access.redhat.com/errata/RHSA-2026:47201
- https://access.redhat.com/security/cve/CVE-2026-45700
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45700.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-mpxh-8fq3-x8mh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45700
- https://bugzilla.redhat.com/show_bug.cgi?id=2483470
