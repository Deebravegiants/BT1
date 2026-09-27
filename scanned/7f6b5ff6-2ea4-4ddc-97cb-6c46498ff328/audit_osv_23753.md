# [M] nvdimm: Fix firmware activation deadlock scenarios

## Summary
Severity: Medium
Advisory: CVE-2022-49446
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49446
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvdimm: Fix firmware activation deadlock scenarios

Lockdep reports the following deadlock scenarios for CXL root device
power-management, device_prepare(), operations, and device_shutdown()
operations for 'nd_region' devices:

 Chain exists of:
   &nvdimm_region_key --> &nvdimm_bus->reconfig_mutex --> system_transition_mutex

  Possible unsafe locking scenario:

        CPU0                    CPU1
        ----                    ----
   lock(system_transition_mutex);
                                lock(&nvdimm_bus->reconfig_mutex);
                                lock(system_transition_mutex);
   lock(&nvdimm_region_key);

 Chain exists of:
   &cxl_nvdimm_bridge_key --> acpi_scan_lock --> &cxl_root_key

  Possible unsafe locking scenario:

        CPU0                    CPU1
        ----                    ----
   lock(&cxl_root_key);
                                lock(acpi_scan_lock);
                                lock(&cxl_root_key);
   lock(&cxl_nvdimm_bridge_key);

These stem from holding nvdimm_bus_lock() over hibernate_quiet_exec()
which walks the entire system device topology taking device_lock() along
the way. The nvdimm_bus_lock() is protecting against unregistration,
multiple simultaneous ops callers, and preventing activate_show() from
racing activate_store(). For the first 2, the lock is redundant.
Unregistration already flushes all ops users, and sysfs already prevents
multiple threads to be active in an ops handler at the same time. For
the last userspace should already be waiting for its last
activate_store() to complete, and does not need activate_show() to flush
the write side, so this lock usage can be deleted in these attributes.

## References
- https://git.kernel.org/stable/c/2f97ebc58d5fc83ca1528cd553fa725472ab3ca8
- https://git.kernel.org/stable/c/2fd853fdb40afc052de338693df1372f2ead7be7
- https://git.kernel.org/stable/c/641649f31e20df630310f5c22f26c071acc676d4
- https://git.kernel.org/stable/c/ceb924ee16b2c8e48dcac3d9ad6be01c40b5a228
- https://git.kernel.org/stable/c/e6829d1bd3c4b58296ee9e412f7ed4d6cb390192
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49446.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49446
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
