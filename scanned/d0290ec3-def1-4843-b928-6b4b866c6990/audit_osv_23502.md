# [H] ipv4: Handle attempt to delete multipath route when fib_info contains an nh reference

## Summary
Severity: High
Advisory: CVE-2022-48999
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48999
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.226, >=5.5.0 <5.10.158, >=5.11.0 <5.15.82, >=5.16.0 <6.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: Handle attempt to delete multipath route when fib_info contains an nh reference

Gwangun Jung reported a slab-out-of-bounds access in fib_nh_match:
    fib_nh_match+0xf98/0x1130 linux-6.0-rc7/net/ipv4/fib_semantics.c:961
    fib_table_delete+0x5f3/0xa40 linux-6.0-rc7/net/ipv4/fib_trie.c:1753
    inet_rtm_delroute+0x2b3/0x380 linux-6.0-rc7/net/ipv4/fib_frontend.c:874

Separate nexthop objects are mutually exclusive with the legacy
multipath spec. Fix fib_nh_match to return if the config for the
to be deleted route contains a multipath spec while the fib_info
is using a nexthop object.

## References
- https://git.kernel.org/stable/c/0b5394229ebae09afc07aabccb5ffd705ffd250e
- https://git.kernel.org/stable/c/25174d91e4a32a24204060d283bd5fa6d0ddf133
- https://git.kernel.org/stable/c/61b91eb33a69c3be11b259c5ea484505cd79f883
- https://git.kernel.org/stable/c/bb20a2ae241be846bc3c11ea4b3a3c69e41d51f2
- https://git.kernel.org/stable/c/cc3cd130ecfb8b0ae52e235e487bae3f16a24a32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48999.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48999
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
