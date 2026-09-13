# [H] libbpf: Reject non-exclusive metadata maps in the signed loader

## Summary
Severity: High
Advisory: CVE-2026-80675
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80675
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

libbpf: Reject non-exclusive metadata maps in the signed loader

The loader verifies map->sha against the metadata hash in its
instructions. map->sha is calculated when BPF_OBJ_GET_INFO_BY_FD is
called on the frozen map.

While the map is frozen, the /signed loader/ must also ensure the map
is exclusive, as, without exclusivity (which a hostile host could just
omit when loading the loader), another BPF program with map access can
mutate the contents afterwards, so the check passes on stale data.

With the extra check as part of the signed loader, it now refuses to
move on with map->sha validation if the host set it up wrongly.

## References
- https://git.kernel.org/stable/c/0dad5adeb34b6f78a883e8faa6a1c947a240e7c9
- https://git.kernel.org/stable/c/0fb6c9ed6493b4af01be8bb0a384574eba7df636
- https://git.kernel.org/stable/c/b6862b6a25c6a925fb0b0e549ee4a52a8d2966fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80675.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80675
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
