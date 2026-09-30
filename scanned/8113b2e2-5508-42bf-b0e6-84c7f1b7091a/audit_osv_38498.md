# [M] libgphoto2 has OOB read in ptp_unpack_DPV() UINT128/INT128 handling in ptp-pack.c

## Summary
Severity: Medium
Advisory: CVE-2026-40335
Aliases: GHSA-g4g5-c2x9-cqfj
CVSS: 5.2 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40335
Type: osv

## Details
libgphoto2 is a camera access and control library. Versions up to and including 2.5.33 have an out-of-bounds read in `ptp_unpack_DPV()` in `camlibs/ptp2/ptp-pack.c` (lines 622–629). The UINT128 and INT128 cases advance `*offset += 16` without verifying that 16 bytes remain in the buffer. The entry check at line 609 only guarantees `*offset < total` (at least 1 byte available), leaving up to 15 bytes unvalidated. Commit 433bde9888d70aa726e32744cd751d7dbe94379a patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40335.json
- https://github.com/gphoto/libgphoto2/security/advisories/GHSA-g4g5-c2x9-cqfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-40335
- https://github.com/gphoto/libgphoto2/commit/433bde9888d70aa726e32744cd751d7dbe94379a
