# [M] ice: fix crash on probe for DPLL enabled E810 LOM

## Summary
Severity: Medium
Advisory: CVE-2024-53048
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53048
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix crash on probe for DPLL enabled E810 LOM

The E810 Lan On Motherboard (LOM) design is vendor specific. Intel
provides the reference design, but it is up to vendor on the final
product design. For some cases, like Linux DPLL support, the static
values defined in the driver does not reflect the actual LOM design.
Current implementation of dpll pins is causing the crash on probe
of the ice driver for such DPLL enabled E810 LOM designs:

WARNING: (...) at drivers/dpll/dpll_core.c:495 dpll_pin_get+0x2c4/0x330
...
Call Trace:
 <TASK>
 ? __warn+0x83/0x130
 ? dpll_pin_get+0x2c4/0x330
 ? report_bug+0x1b7/0x1d0
 ? handle_bug+0x42/0x70
 ? exc_invalid_op+0x18/0x70
 ? asm_exc_invalid_op+0x1a/0x20
 ? dpll_pin_get+0x117/0x330
 ? dpll_pin_get+0x2c4/0x330
 ? dpll_pin_get+0x117/0x330
 ice_dpll_get_pins.isra.0+0x52/0xe0 [ice]
...

The number of dpll pins enabled by LOM vendor is greater than expected
and defined in the driver for Intel designed NICs, which causes the crash.

Prevent the crash and allow generic pin initialization within Linux DPLL
subsystem for DPLL enabled E810 LOM designs.

Newly designed solution for described issue will be based on "per HW
design" pin initialization. It requires pin information dynamically
acquired from the firmware and is already in progress, planned for
next-tree only.

## References
- https://git.kernel.org/stable/c/6e58c33106220c6c0c8fbee9ab63eae76ad8f260
- https://git.kernel.org/stable/c/82b107a27bab29146e159b6b9f21146c97c45a53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53048.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53048
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
