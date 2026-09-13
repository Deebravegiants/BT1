# [M] CVE-2021-47060

## Summary
Severity: Medium
Advisory: CVE-2021-47060
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47060
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: Stop looking for coalesced MMIO zones if the bus is destroyed

Abort the walk of coalesced MMIO zones if kvm_io_bus_unregister_dev()
fails to allocate memory for the new instance of the bus.  If it can't
instantiate a new bus, unregister_dev() destroys all devices _except_ the
target device.   But, it doesn't tell the caller that it obliterated the
bus and invoked the destructor for all devices that were on the bus.  In
the coalesced MMIO case, this can result in a deleted list entry
dereference due to attempting to continue iterating on coalesced_zones
after future entries (in the walk) have been deleted.

Opportunistically add curly braces to the for-loop, which encompasses
many lines but sneaks by without braces due to the guts being a single
if statement.

## References
- https://git.kernel.org/stable/c/168e82f640ed1891a700bdb43e37da354b2ab63c
- https://git.kernel.org/stable/c/2a20592baff59c5351c5200ec667e1a2aa22af85
- https://git.kernel.org/stable/c/50cbad42bfea8c052b7ca590bd4126cdc898713c
- https://git.kernel.org/stable/c/5d3c4c79384af06e3c8e25b7770b6247496b4417
- https://git.kernel.org/stable/c/7d1bc32d6477ff96a32695ea4be8144e4513ab2d
