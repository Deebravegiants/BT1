# [H] hwmon: (nct6775-core) Prevent access to unsupported weight registers

## Summary
Severity: High
Advisory: CVE-2026-74549
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74549
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (nct6775-core) Prevent access to unsupported weight registers

Sashiko reports:

During initialization of the nct6116 chip, the driver sets data->pwm_num
to 5. However, it assigns several NCT6106 register arrays (such as
NCT6106_REG_WEIGHT_DUTY_STEP, NCT6106_REG_WEIGHT_TEMP_SEL, and
NCT6106_REG_WEIGHT_TEMP_*) to data->REG_PWM and data->REG_WEIGHT_TEMP.
These arrays only contain 3 elements.

In nct6775_update_pwm(), the driver iterates up to data->pwm_num. If
data->has_pwm has bits 3 or 4 set (which is structurally possible for
nct6116), the loop attempts to read elements at index 3 and 4 from these
3-element arrays. This results in a global out-of-bounds read, which can
be caught by KASAN.

Furthermore, the driver uses these garbage out-of-bounds values as
hardware register addresses for subsequent read and write operations. This
leads to invalid hardware register access, potentially causing hardware
misconfiguration or system crashes.

The underlying problem is that the chip does support up to five fan
control channels, but only the first three support weight control.
Fix the problem by extending the affected weight register arrays with
zeroed fields. The driver uses zeroed register addresses to determine
if a register is supported or not, and skips accesses for unsupported
registers.

## References
- https://git.kernel.org/stable/c/0d11b2a10269ace29832f584d207ff3768f79dc5
- https://git.kernel.org/stable/c/1b722740ac5c2b2070f9ba922f4e0f227faf0246
- https://git.kernel.org/stable/c/25b528816f5d83be5236dc182692369e8c9402b0
- https://git.kernel.org/stable/c/4a77f1d72c6db04cbbfab0250292ac71fdea5f0a
- https://git.kernel.org/stable/c/4ad2972ef0e1bd1018ad7a72661a4636ed7daecc
- https://git.kernel.org/stable/c/513d847f7a95bbdbeaaf55fb942c38992587734f
- https://git.kernel.org/stable/c/689082a4cb166a7ae9729f7b12339e69fdad6c52
- https://git.kernel.org/stable/c/d0b704e569ac3b8416d8e02270cdc9bf830ed395
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74549.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74549
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
