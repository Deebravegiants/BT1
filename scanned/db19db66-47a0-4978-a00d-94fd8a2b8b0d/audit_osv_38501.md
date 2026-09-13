# [M] libgphoto2 has OOB read in ptp_unpack_OI() in ptp-pack.c via malicious PTP ObjectInfo response

## Summary
Severity: Medium
Advisory: CVE-2026-40340
Aliases: GHSA-xfw3-xvjp-5wcv
CVSS: 6.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40340
Type: osv

## Details
libgphoto2 is a camera access and control library. Versions up to and including 2.5.33 have an out-of-bounds read vulnerability in `ptp_unpack_OI()` in `camlibs/ptp2/ptp-pack.c` (lines 530–563). The function validates `len < PTP_oi_SequenceNumber` (i.e., len < 48) but subsequently accesses offsets 48–56, up to 9 bytes beyond the validated boundary, via the Samsung Galaxy 64-bit objectsize detection heuristic. Commit 7c7f515bc88c3d0c4098ac965d313518e0ccbe33 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40340.json
- https://github.com/gphoto/libgphoto2/security/advisories/GHSA-xfw3-xvjp-5wcv
- https://nvd.nist.gov/vuln/detail/CVE-2026-40340
- https://github.com/gphoto/libgphoto2/commit/7c7f515bc88c3d0c4098ac965d313518e0ccbe33
