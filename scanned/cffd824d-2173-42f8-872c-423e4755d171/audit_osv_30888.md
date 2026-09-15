# [M] irqchip/riscv-aplic: Prevent crash when MSI domain is missing

## Summary
Severity: Medium
Advisory: CVE-2024-56682
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56682
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/riscv-aplic: Prevent crash when MSI domain is missing

If the APLIC driver is probed before the IMSIC driver, the parent MSI
domain will be missing, which causes a NULL pointer dereference in
msi_create_device_irq_domain().

Avoid this by deferring probe until the parent MSI domain is available. Use
dev_err_probe() to avoid printing an error message when returning
-EPROBE_DEFER.

## References
- https://git.kernel.org/stable/c/1f181d1cda56c2fbe379c5ace1aa1fac6306669e
- https://git.kernel.org/stable/c/285a07810ab3bcedc2bd380ebacbf6b4942a889a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56682.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56682
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
