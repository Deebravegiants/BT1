# [H] perf/core: Fix perf_output_begin parameter is incorrectly invoked in perf_event_bpf_output

## Summary
Severity: High
Advisory: CVE-2023-53065
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53065
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.177, >=5.11.0 <5.15.105, >=5.16.0 <6.1.22, >=6.2.0 <6.2.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/core: Fix perf_output_begin parameter is incorrectly invoked in perf_event_bpf_output

syzkaller reportes a KASAN issue with stack-out-of-bounds.
The call trace is as follows:
  dump_stack+0x9c/0xd3
  print_address_description.constprop.0+0x19/0x170
  __kasan_report.cold+0x6c/0x84
  kasan_report+0x3a/0x50
  __perf_event_header__init_id+0x34/0x290
  perf_event_header__init_id+0x48/0x60
  perf_output_begin+0x4a4/0x560
  perf_event_bpf_output+0x161/0x1e0
  perf_iterate_sb_cpu+0x29e/0x340
  perf_iterate_sb+0x4c/0xc0
  perf_event_bpf_event+0x194/0x2c0
  __bpf_prog_put.constprop.0+0x55/0xf0
  __cls_bpf_delete_prog+0xea/0x120 [cls_bpf]
  cls_bpf_delete_prog_work+0x1c/0x30 [cls_bpf]
  process_one_work+0x3c2/0x730
  worker_thread+0x93/0x650
  kthread+0x1b8/0x210
  ret_from_fork+0x1f/0x30

commit 267fb27352b6 ("perf: Reduce stack usage of perf_output_begin()")
use on-stack struct perf_sample_data of the caller function.

However, perf_event_bpf_output uses incorrect parameter to convert
small-sized data (struct perf_bpf_event) into large-sized data
(struct perf_sample_data), which causes memory overwriting occurs in
__perf_event_header__init_id.

## References
- https://git.kernel.org/stable/c/3a776fddb4e5598c8bfcd4ad094fba34f9856fc9
- https://git.kernel.org/stable/c/ac5f88642cb211152041f84a985309e9af4baf59
- https://git.kernel.org/stable/c/ddcf8320003638a06eb1e46412e045d0c5701575
- https://git.kernel.org/stable/c/eb81a2ed4f52be831c9fb879752d89645a312c13
- https://git.kernel.org/stable/c/ff8137727a2af4ad5f6e6c8b9f7ec5e8db9da86c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53065.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53065
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
