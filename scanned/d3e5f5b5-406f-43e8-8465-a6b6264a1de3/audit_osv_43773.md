# [H] vhost_iotlb: bound map allocation in add_range

## Summary
Severity: High
Advisory: CVE-2026-74713
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74713
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost_iotlb: bound map allocation in add_range

vhost_iotlb_add_range_ctx() only retires an old entry when the table
has a non-zero limit, has exactly reached that limit and has
VHOST_IOTLB_FLAG_RETIRE set. Non-retiring tables can keep allocating
entries after reaching their configured limit.

Existing vhost devices allocate their IOTLB with max_iotlb_entries from
vhost.c, which defaults to 2048 and is tunable by module parameter. Use
the caller-provided limit at the allocation point instead of adding a
separate default in the common IOTLB helper, and reject non-positive
values in vhost paths that can report an error.

Other vhost IOTLB users should not create zero-limit tables when entries
can be populated from userspace or guest-controlled requests. Add
caller-side max_iotlb_entries parameters for mlx5 vDPA, VDUSE and
vhost-vDPA. Reject non-positive VDUSE and vhost-vDPA values, and require
at least two entries for vdpa_sim and mlx5 vDPA paths that install
full-range mappings, since those mappings are split into two IOTLB
entries.

Handle full-range mappings in the common helper by checking that the
IOTLB can hold both split entries before inserting the first half. This
avoids returning an error after leaving a half mapping behind.

When the table is full, keep the existing retire behavior for retiring
tables and return -ENOSPC for non-retiring tables. Reuse the retired map
node instead of freeing it and allocating a replacement, so a stream of
IOTLB updates cannot keep forcing GFP_ATOMIC allocations after the table
has reached its limit. If a zero-limit IOTLB still reaches the common
helper, treat it as a configuration error and return -EINVAL.

I found this bug myself, though the patch was written with AI assistance.

## References
- https://git.kernel.org/stable/c/1ed35ac7f3fe2b4396bdd29ac3a7f0ebc0829e94
- https://git.kernel.org/stable/c/ae128dd19040ee06a4f8143c7ced4d18080d7a9a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74713.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74713
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
