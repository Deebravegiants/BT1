# [H] keys: fix out-of-bounds read in keyring_get_key_chunk()

## Summary
Severity: High
Advisory: CVE-2026-74567
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74567
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

keys: fix out-of-bounds read in keyring_get_key_chunk()

For description-level chunks keyring_get_key_chunk() advances the read
pointer by level * sizeof(long) past the inline prefix but only
bounds-checks the prefix, so a long enough key description is read past
its kmemdup(desc, desc_len + 1) allocation.  Compute the full byte
offset and bounds-check the description against it before reading.

The walk only reaches a description-level chunk when two keys collide
through the hash, x, type and domain_tag chunks, so this is reached from
an unprivileged add_key(2) with a crafted pair of same-type keys whose
index hashes collide; KASAN reports a slab-out-of-bounds read.

## References
- https://git.kernel.org/stable/c/3a744838453fb9309ce5a5526d3252e211d60152
- https://git.kernel.org/stable/c/4c0c26f751e50d3027eacc4d7d0fabc31f1d7e6b
- https://git.kernel.org/stable/c/63918731f9ae25b5deb022f118e941e6dddfcef4
- https://git.kernel.org/stable/c/79916f40d4ab1b4ae694d8c024fd179454bfe46e
- https://git.kernel.org/stable/c/8dba33c1e779d0fb9a2acb31e354cf0fc0229111
- https://git.kernel.org/stable/c/d1933e03e8c74a018550c31a393b79c4d95bff40
- https://git.kernel.org/stable/c/e5b01998cef8d7f613200230ccaadebe5de9135c
- https://git.kernel.org/stable/c/e9417d21a22ad2ec398e78fcf084b717ce92cf2f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74567.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74567
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
