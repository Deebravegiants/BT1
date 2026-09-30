# [M] Bluetooth: btrtl: check for NULL in btrtl_setup_realtek()

## Summary
Severity: Medium
Advisory: CVE-2024-57987
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57987
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btrtl: check for NULL in btrtl_setup_realtek()

If insert an USB dongle which chip is not maintained in ic_id_table, it
will hit the NULL point accessed. Add a null point check to avoid the
Kernel Oops.

## References
- https://git.kernel.org/stable/c/02f9da874e5e4626f81772eacc18967921998a71
- https://git.kernel.org/stable/c/1158ad8e8abb361d4b2aaa010c9af74de20ab82b
- https://git.kernel.org/stable/c/3c15082f3567032d196e8760753373332508c2ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57987.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57987
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
