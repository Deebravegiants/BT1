# [H] thermal: core: Reference count the zone in thermal_zone_get_by_id()

## Summary
Severity: High
Advisory: CVE-2024-50028
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-50028
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal: core: Reference count the zone in thermal_zone_get_by_id()

There are places in the thermal netlink code where nothing prevents
the thermal zone object from going away while being accessed after it
has been returned by thermal_zone_get_by_id().

To address this, make thermal_zone_get_by_id() get a reference on the
thermal zone device object to be returned with the help of get_device(),
under thermal_list_lock, and adjust all of its callers to this change
with the help of the cleanup.h infrastructure.

## References
- https://git.kernel.org/stable/c/a42a5839f400e929c489bb1b58f54596c4535167
- https://git.kernel.org/stable/c/c95538b286efc6109c987e97a051bc7844ede802
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50028.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50028
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
