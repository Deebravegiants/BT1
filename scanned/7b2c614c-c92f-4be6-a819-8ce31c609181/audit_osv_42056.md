# [H] netfilter: ebtables: terminate table name before find_table_lock()

## Summary
Severity: High
Advisory: CVE-2026-64411
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64411
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ebtables: terminate table name before find_table_lock()

update_counters() and compat_update_counters() forward a user-supplied
32-byte table name to find_table_lock() without NUL-terminating it. On a
lookup miss, find_inlist_lock() calls try_then_request_module(..., "%s%s",
"ebtable_", name), and vsnprintf() reads past the name field and the
stack object until it hits a zero byte.

  BUG: KASAN: stack-out-of-bounds in string (lib/vsprintf.c:648 lib/vsprintf.c:730)
  Read of size 1 at addr ffff8880119dfb20 by task exploit/147
  Call Trace:
  ...
   string (lib/vsprintf.c:648 lib/vsprintf.c:730)
   vsnprintf (lib/vsprintf.c:2945)
   __request_module (kernel/module/kmod.c:150)
   do_update_counters.isra.0 (net/bridge/netfilter/ebtables.c:371 net/bridge/netfilter/ebtables.c:380)
   update_counters (net/bridge/netfilter/ebtables.c:1440)
   do_ebt_set_ctl (net/bridge/netfilter/ebtables.c:2573)
   nf_setsockopt (net/netfilter/nf_sockopt.c:101)
   ip_setsockopt (net/ipv4/ip_sockglue.c:1424)
   raw_setsockopt (net/ipv4/raw.c:847)
   __sys_setsockopt (net/socket.c:2393)
  ...

compat_do_replace() shares the same unterminated name via
compat_copy_ebt_replace_from_user(); terminate it there too so all
find_table_lock() callers behave alike. The other callers already
terminate the name after the copy.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/2664f537ca5bcb2ef3fac2683dcca602e51fad24
- https://git.kernel.org/stable/c/4c046ca4e35a83ea32f6e748f54139f5fe2a1d01
- https://git.kernel.org/stable/c/6fe8d3cecd20bfaaaf440db3a06ba674d2f2e322
- https://git.kernel.org/stable/c/7436da6c1bc44654b7f11a17e746f6999fd37250
- https://git.kernel.org/stable/c/a622d2e9608c9dff47fc2e5759ac7aa3a836b45d
- https://git.kernel.org/stable/c/ab63ccefb9c71627f957a0724c2b9ebc869c6f20
- https://git.kernel.org/stable/c/b6183b1b88a722b6d8ea0cecc99eba168a15e0be
- https://git.kernel.org/stable/c/c6f539311e58e76aa96feef0f1572b13a564f8a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64411.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64411
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
