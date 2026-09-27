# [C] RT-Thread device.c sys_device_write memory corruption

## Summary
Severity: Critical
Advisory: CVE-2025-6693
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X)
Published: 2025-06-26
Source: https://osv.dev/vulnerability/CVE-2025-6693
Type: osv

## Details
A vulnerability, which was classified as critical, was found in RT-Thread up to 5.1.0. This affects the function sys_device_open/sys_device_read/sys_device_control/sys_device_init/sys_device_close/sys_device_write of the file components/drivers/core/device.c. The manipulation leads to memory corruption. It is possible to launch the attack on the local host. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6693.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6693
- https://vuldb.com/?id.313959
- https://vuldb.com/?submit.595813
- https://vuldb.com/?submit.595814
- https://vuldb.com/?submit.595827
- https://vuldb.com/?submit.595869
- https://vuldb.com/?submit.595870
- https://vuldb.com/?submit.595871
- https://github.com/RT-Thread/rt-thread/issues/10387
- https://vuldb.com/?ctiid.313959
