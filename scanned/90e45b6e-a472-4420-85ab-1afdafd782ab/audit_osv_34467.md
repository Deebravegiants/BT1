# [M] CVE-2025-60468

## Summary
Severity: Medium
Advisory: CVE-2025-60468
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2025-60468
Type: osv

## Details
GPAC Multimedia Open Source Project GPAC Project/MP4Box 2.5-DEV-rev1593-gfe88c3545-master is affected by: Buffer Overflow. The impact is: cause a denial of service (local). The component is: filter_core/filter_pid.c (L:574-580): function gf_filter_pid_inst_swap_delete_task() improperly accesses freed objects during PID instance swap/delete cleanup, leading to heap use-after-free. The attack vector is: Local (AV:L): a local, authenticated user who processes a specially crafted MPEG-2 TS/MP4 file with MP4Box can trigger the bug during filter teardown (PID instance swap/delete), causing a crash. ¶¶ In GPAC s MP4Box, gf_filter_pid_inst_swap_delete_task() in filter_core/filter_pid.c may dereference objects after they have been freed when cleaning up PID instances after a swap/delete operation. Crafted inputs (e.g., malformed MPEG-2 TS) can trigger a heap use-after-free and crash; exploitation may be possible.

## References
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/39/39_gf_filter_pid_inst_swap_delete_task_filter_core_filter_pid_c_580
- https://infosec.exchange/@sigdevel/116780598378458041
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60468.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60468
- https://github.com/gpac/gpac/issues/3290
- https://github.com/gpac/gpac/commit/976dacf65cb6986a4e4f350fb8d3ed0a17dc3a77
- https://github.com/gpac/gpac/commit/aed9c94e92e8ba362ddb29c767c519478f46f195
