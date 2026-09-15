# [C] ipv6: ioam: fix type confusion of dst_entry

## Summary
Severity: Critical
Advisory: CVE-2026-72429
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72429
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: ioam: fix type confusion of dst_entry

IOAM uses a dummy dst_entry(null_dst) to mark that the destination should
not be changed after the transformation. This dst is stored in the IOAM lwt
state and may be passed to dst_cache_set_ip6().

However, the IPv6 dst cache path eventually calls rt6_get_cookie(), which
treats the dst_entry as part of a struct rt6_info. Since the null_dst was
embedded directly as a struct dst_entry in struct ioam6_lwt, this resulted
in an invalid cast and rt6_get_cookie() reading fields from the wrong
object.

In practice, the wrong cookie is not used while dst->obsolete is zero, but
rt6_get_cookie() may also access per-cpu value when rt->sernum is
zero. In this case, rt->sernum aliases ioam6_lwt::cache::reset_ts, which
can become zero, making this a potential invalid pointer access.

Fix this by embedding a full struct rt6_info for the dummy IPv6 route and
passing its dst member to the dst APIs.

## References
- https://git.kernel.org/stable/c/5a3b2ee1e96d0580a8ed8deda6dfa430604f9ab0
- https://git.kernel.org/stable/c/9ed19e11d2146076d117d51a940643990118449b
- https://git.kernel.org/stable/c/ea24f911ead85ba3d570a31e37c52b6c949f6928
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72429.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72429
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
