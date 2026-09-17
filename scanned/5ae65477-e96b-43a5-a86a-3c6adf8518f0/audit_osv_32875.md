# [H] tipc: fix null-ptr-deref when acquiring remote ip of ethernet bearer

## Summary
Severity: High
Advisory: CVE-2025-38184
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38184
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix null-ptr-deref when acquiring remote ip of ethernet bearer

The reproduction steps:
1. create a tun interface
2. enable l2 bearer
3. TIPC_NL_UDP_GET_REMOTEIP with media name set to tun

tipc: Started in network mode
tipc: Node identity 8af312d38a21, cluster identity 4711
tipc: Enabled bearer <eth:syz_tun>, priority 1
Oops: general protection fault
KASAN: null-ptr-deref in range
CPU: 1 UID: 1000 PID: 559 Comm: poc Not tainted 6.16.0-rc1+ #117 PREEMPT
Hardware name: QEMU Ubuntu 24.04 PC
RIP: 0010:tipc_udp_nl_dump_remoteip+0x4a4/0x8f0

the ub was in fact a struct dev.

when bid != 0 && skip_cnt != 0, bearer_list[bid] may be NULL or
other media when other thread changes it.

fix this by checking media_id.

## References
- https://git.kernel.org/stable/c/05d332ba075753d569d66333d62d60fff5f57ad8
- https://git.kernel.org/stable/c/0d3d91c3500f0c480e016faa4e2259c588616e59
- https://git.kernel.org/stable/c/0f4a72fb266e48dbe928e1d936eab149e4ac3e1b
- https://git.kernel.org/stable/c/3998283e4c32c0fe69edd59b0876c193f50abce6
- https://git.kernel.org/stable/c/8595350615f952fcf8bc861464a6bf6b1129af50
- https://git.kernel.org/stable/c/c2e17984752b9131061d1a2ca1199da2706337fd
- https://git.kernel.org/stable/c/d3dfe821dfe091c0045044343c8d86596d66e2cf
- https://git.kernel.org/stable/c/f82727adcf2992822e12198792af450a76ebd5ef
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38184.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38184
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
