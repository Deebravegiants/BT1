# [M] CVE-2025-55639

## Summary
Severity: Medium
Advisory: CVE-2025-55639
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2025-55639
Type: osv

## Details
GPAC MP4Box v2.4 was discovered to contain a NULL pointer dereference in the gf_isom_add_track_kind() function at isomedia/isom_write.c. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted MP4 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/26/2
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/23/23_poc.mp4
- https://infosec.exchange/@sigdevel/116769184815236865
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55639.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55639
- https://github.com/gpac/gpac/issues/3260
- https://github.com/gpac/gpac/commit/027ce139dda498ee95df36db9f9f6f3cadce8ec9
