# [M] CVE-2025-60465

## Summary
Severity: Medium
Advisory: CVE-2025-60465
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2025-60465
Type: osv

## Details
A use-after-free in the gf_filter_pid_inst_swap function (/filter_core/filter_pid.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted media file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/27/1
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/34/34_gf_filter_pid_inst_swap_filter_core_filter_pid_c_633
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/34/README.md
- https://infosec.exchange/@sigdevel/116778494176930561
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60465.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60465
- https://github.com/gpac/gpac/issues/3283
- https://github.com/gpac/gpac/commit/55b351bd078c950592544ab4c708a613c1725b9b
