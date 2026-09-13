# [M] CVE-2025-60471

## Summary
Severity: Medium
Advisory: CVE-2025-60471
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2025-60471
Type: osv

## Details
A use-after-free in the gf_filter_pid_reconfigure_task_discard function (/filter_core/filter_pid.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted media file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/26/3
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/31/31_gf_filter_pid_reconfigure_task_discard_filter_core_filter_pid_c_1341
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/31/README.md
- https://infosec.exchange/@sigdevel/116778301425195980
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60471.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60471
- https://github.com/gpac/gpac/issues/3279
- https://github.com/gpac/gpac/commit/868c6801c226e9964cace54cfd5a759f152780b4
