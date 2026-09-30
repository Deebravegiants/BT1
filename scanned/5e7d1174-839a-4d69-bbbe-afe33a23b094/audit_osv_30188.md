# [M] bpf: Make sure internal and UAPI bpf_redirect flags don't overlap

## Summary
Severity: Medium
Advisory: CVE-2024-50163
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50163
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Make sure internal and UAPI bpf_redirect flags don't overlap

The bpf_redirect_info is shared between the SKB and XDP redirect paths,
and the two paths use the same numeric flag values in the ri->flags
field (specifically, BPF_F_BROADCAST == BPF_F_NEXTHOP). This means that
if skb bpf_redirect_neigh() is used with a non-NULL params argument and,
subsequently, an XDP redirect is performed using the same
bpf_redirect_info struct, the XDP path will get confused and end up
crashing, which syzbot managed to trigger.

With the stack-allocated bpf_redirect_info, the structure is no longer
shared between the SKB and XDP paths, so the crash doesn't happen
anymore. However, different code paths using identically-numbered flag
values in the same struct field still seems like a bit of a mess, so
this patch cleans that up by moving the flag definitions together and
redefining the three flags in BPF_F_REDIRECT_INTERNAL to not overlap
with the flags used for XDP. It also adds a BUILD_BUG_ON() check to make
sure the overlap is not re-introduced by mistake.

## References
- https://git.kernel.org/stable/c/09d88791c7cd888d5195c84733caf9183dcfbd16
- https://git.kernel.org/stable/c/0fca5ed4be8e8bfbfb9bd97845af596bab7192d3
- https://git.kernel.org/stable/c/314dbee9fe4f5cee36435465de52c988d7caa466
- https://git.kernel.org/stable/c/4e1e428533845d48828bd3875c0e92e8565b9962
- https://git.kernel.org/stable/c/cec288e05ceac9a0d3a3a1fd279534b11844c826
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50163.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50163
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
