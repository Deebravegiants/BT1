# [H] net/sched: cls_bpf: reject dev-bound programs bound to a different device

## Summary
Severity: High
Advisory: CVE-2026-74736
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74736
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: cls_bpf: reject dev-bound programs bound to a different device

cls_bpf_prog_from_efd() obtained a SCHED_CLS program via
bpf_prog_get_type_dev() but never verified that a device-bound (offloaded)
program's bound netdev matches the TC netdev the classifier is being
attached to. This let a program loaded with prog_ifindex for device A be
attached via cls_bpf + skip_sw to device B; deleting device A then
destroyed the program's offload state while it was still attached to
device B, triggering a netdevsim WARN (panic with panic_on_warn=1).

Mirror the XDP attach path (net/core/dev.c) and reject the attach with
-EINVAL when a dev-bound program's bound device does not match the
target device.

## References
- https://git.kernel.org/stable/c/120977e2c096deea4e866e4273be9220b957c29e
- https://git.kernel.org/stable/c/5685bbbd3cbfbeb0de96a1d275a5ca073dfebb5e
- https://git.kernel.org/stable/c/adb3e7c26a51a10d94a241c6de7a81a2863dcacf
- https://git.kernel.org/stable/c/daf546ab5763ce6a18280cb4db060e836c515301
- https://git.kernel.org/stable/c/ec5a552f4b2d841c6c021752450716e1a9676661
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74736.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74736
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
