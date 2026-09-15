# [M] ftrace: Fix regression with module command in stack_trace_filter

## Summary
Severity: Medium
Advisory: CVE-2024-56569
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56569
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ftrace: Fix regression with module command in stack_trace_filter

When executing the following command:

    # echo "write*:mod:ext3" > /sys/kernel/tracing/stack_trace_filter

The current mod command causes a null pointer dereference. While commit
0f17976568b3f ("ftrace: Fix regression with module command in stack_trace_filter")
has addressed part of the issue, it left a corner case unhandled, which still
results in a kernel crash.

## References
- https://git.kernel.org/stable/c/19cacabdd5a8487ae566cbecb4d03bcb038a067e
- https://git.kernel.org/stable/c/43ca32ce12888fb0eeb2d74dfc558dea60d3473e
- https://git.kernel.org/stable/c/45af52e7d3b8560f21d139b3759735eead8b1653
- https://git.kernel.org/stable/c/5dabb7af57bc72308a6e2e81a5dd756eef283803
- https://git.kernel.org/stable/c/7ae27880de3482e063fcc1f72d9a298d0d391407
- https://git.kernel.org/stable/c/885109aa0c70639527dd6a65c82e63c9ac055e3d
- https://git.kernel.org/stable/c/8a92dc4df89c50bdb26667419ea70e0abbce456e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56569.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56569
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
