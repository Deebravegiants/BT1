# [H] dm: Always split write BIOs to zoned device limits

## Summary
Severity: High
Advisory: CVE-2025-39792
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-12
Source: https://osv.dev/vulnerability/CVE-2025-39792
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm: Always split write BIOs to zoned device limits

Any zoned DM target that requires zone append emulation will use the
block layer zone write plugging. In such case, DM target drivers must
not split BIOs using dm_accept_partial_bio() as doing so can potentially
lead to deadlocks with queue freeze operations. Regular write operations
used to emulate zone append operations also cannot be split by the
target driver as that would result in an invalid writen sector value
return using the BIO sector.

In order for zoned DM target drivers to avoid such incorrect BIO
splitting, we must ensure that large BIOs are split before being passed
to the map() function of the target, thus guaranteeing that the
limits for the mapped device are not exceeded.

dm-crypt and dm-flakey are the only target drivers supporting zoned
devices and using dm_accept_partial_bio().

In the case of dm-crypt, this function is used to split BIOs to the
internal max_write_size limit (which will be suppressed in a different
patch). However, since crypt_alloc_buffer() uses a bioset allowing only
up to BIO_MAX_VECS (256) vectors in a BIO. The dm-crypt device
max_segments limit, which is not set and so default to BLK_MAX_SEGMENTS
(128), must thus be respected and write BIOs split accordingly.

In the case of dm-flakey, since zone append emulation is not required,
the block layer zone write plugging is not used and no splitting of BIOs
required.

Modify the function dm_zone_bio_needs_split() to use the block layer
helper function bio_needs_zone_write_plugging() to force a call to
bio_split_to_limits() in dm_split_and_process_bio(). This allows DM
target drivers to avoid using dm_accept_partial_bio() for write
operations on zoned DM devices.

## References
- https://git.kernel.org/stable/c/2df7168717b7d2d32bcf017c68be16e4aae9dd13
- https://git.kernel.org/stable/c/4e9fef1cf0243d665d75c371cc80be6156cd30a2
- https://git.kernel.org/stable/c/d10bf66d9f9335ffc7521b3029b114f50604cabe
- https://git.kernel.org/stable/c/f5dd256333c08ab44b5aec4a8118cb04c0f20c54
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39792.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39792
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
