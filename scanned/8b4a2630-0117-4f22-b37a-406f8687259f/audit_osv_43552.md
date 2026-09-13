# [H] bpf: Reject exclusive maps as inner maps in map-in-map

## Summary
Severity: High
Advisory: CVE-2026-74364
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74364
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reject exclusive maps as inner maps in map-in-map

An exclusive map (created with excl_prog_hash) is bound to a single
program by hash: check_map_prog_compatibility() refuses to load any
program whose digest does not match map->excl_prog_sha. That check
only runs for maps a program references directly, i.e. its used_maps.
A map reached at runtime through a map-of-maps is never in used_maps,
and bpf_map_meta_equal() does not consider excl_prog_sha, so an
exclusive map can be inserted into a non-exclusive outer map and
then looked up and mutated by an unrelated program, bypassing the
exclusivity guarantee.

For the signed loader this defeats the metadata map exclusivity check
added in the signed loader: the cached map->sha[] is validated against
the signed hash while another program on a hostile host rewrites the
frozen map's contents through the outer map.

## References
- https://git.kernel.org/stable/c/3a0f73d27a8d379a8852a378b3c3208143e3b3b2
- https://git.kernel.org/stable/c/7c58ace08f180f8e249e714d1623388362f9d807
- https://git.kernel.org/stable/c/9a3c3c49c333760c8944dadacbe114c1884546ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74364.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74364
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
