# [M] libgphoto2 has OOB read in ptp_unpack_Sony_DPD() enumeration count parsing in ptp-pack.c

## Summary
Severity: Medium
Advisory: CVE-2026-40338
Aliases: GHSA-2hwp-w84q-27hf
CVSS: 5.2 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40338
Type: osv

## Details
libgphoto2 is a camera access and control library. Versions up to and including 2.5.33 have an out-of-bounds read in the PTP_DPFF_Enumeration case of `ptp_unpack_Sony_DPD()` in `camlibs/ptp2/ptp-pack.c` (line 856). The function reads a 2-byte enumeration count N via `dtoh16o(data, *poffset)` without verifying that 2 bytes remain in the buffer. The standard `ptp_unpack_DPD()` at line 704 has this exact check, confirming the Sony variant omitted it by oversight. Commit 3b9f9696be76ae51dca983d9dd8ce586a2561845 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40338.json
- https://github.com/gphoto/libgphoto2/security/advisories/GHSA-2hwp-w84q-27hf
- https://nvd.nist.gov/vuln/detail/CVE-2026-40338
- https://github.com/gphoto/libgphoto2/commit/3b9f9696be76ae51dca983d9dd8ce586a2561845
