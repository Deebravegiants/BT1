# [M] CVE-2025-60466

## Summary
Severity: Medium
Advisory: CVE-2025-60466
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2025-60466
Type: osv

## Details
A use-after-free in the gf_filter_pid_get_packet function (/filter_core/filter_pid.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted media file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/27/2
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/35/35_gf_filter_pid_get_packet_filter_core_filter_pid_c_6827
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/35/README.md
- https://infosec.exchange/@sigdevel/116780402249845037
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60466.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60466
- https://github.com/gpac/gpac/issues/3284
- https://github.com/gpac/gpac/commit/4a7ea06dd1b2cc65fe0dabc60189eb6bc814f7bb
