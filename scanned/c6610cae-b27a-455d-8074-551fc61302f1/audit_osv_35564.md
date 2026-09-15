# [M] NULL pointer dereference in Zephyr Dhara FTL disk driver on flash read error during journal resume

## Summary
Severity: Medium
Advisory: CVE-2026-10659
Aliases: GHSA-q28v-3729-f82g
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-10659
Type: osv

## Details
The Dhara flash translation layer disk driver (drivers/disk/ftl_dhara.c) implemented the dhara_nand_ callbacks so that, on a flash error, the error code was written unconditionally through the caller-supplied dhara_error_t err pointer (e.g. *err = DHARA_E_ECC in dhara_nand_read, and similar in dhara_nand_erase/prog/copy).

The upstream Dhara library calls these callbacks with err == NULL along its journal-resume binary search: find_last_checkblock() invokes find_checkblock(j, mid, &found, NULL), which forwards the NULL pointer into dhara_nand_read(). This path runs during disk_ftl_access_init() -> dhara_map_resume() whenever the FTL disk is mounted/initialised.

If a flash read error (uncorrectable ECC, bad block, controller error) occurs on one of the probed checkpoint pages, the driver dereferences and writes to NULL, faulting the kernel (denial of service). The trigger is conditioned on the NAND medium content/health, which can be influenced by media wear, induced faults, or a corrupted/crafted on-flash image.

The fix routes all error assignments through the library's NULL-safe dhara_set_error() helper. Affects Zephyr v4.4.0, where the driver was introduced.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10659.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-q28v-3729-f82g
- https://nvd.nist.gov/vuln/detail/CVE-2026-10659
- https://github.com/zephyrproject-rtos/zephyr/commit/a8371b0d4719efe37a66e2abb618ad9b81792212
- https://github.com/zephyrproject-rtos/zephyr
