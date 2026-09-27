# [H] ACPICA: Fix use-after-free in acpi_ut_copy_ipackage_to_ipackage()

## Summary
Severity: High
Advisory: CVE-2022-50423
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2022-50423
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPICA: Fix use-after-free in acpi_ut_copy_ipackage_to_ipackage()

There is an use-after-free reported by KASAN:

  BUG: KASAN: use-after-free in acpi_ut_remove_reference+0x3b/0x82
  Read of size 1 at addr ffff888112afc460 by task modprobe/2111
  CPU: 0 PID: 2111 Comm: modprobe Not tainted 6.1.0-rc7-dirty
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996),
  Call Trace:
   <TASK>
   kasan_report+0xae/0xe0
   acpi_ut_remove_reference+0x3b/0x82
   acpi_ut_copy_iobject_to_iobject+0x3be/0x3d5
   acpi_ds_store_object_to_local+0x15d/0x3a0
   acpi_ex_store+0x78d/0x7fd
   acpi_ex_opcode_1A_1T_1R+0xbe4/0xf9b
   acpi_ps_parse_aml+0x217/0x8d5
   ...
   </TASK>

The root cause of the problem is that the acpi_operand_object
is freed when acpi_ut_walk_package_tree() fails in
acpi_ut_copy_ipackage_to_ipackage(), lead to repeated release in
acpi_ut_copy_iobject_to_iobject(). The problem was introduced
by "8aa5e56eeb61" commit, this commit is to fix memory leak in
acpi_ut_copy_iobject_to_iobject(), repeatedly adding remove
operation, lead to "acpi_operand_object" used after free.

Fix it by removing acpi_ut_remove_reference() in
acpi_ut_copy_ipackage_to_ipackage(). acpi_ut_copy_ipackage_to_ipackage()
is called to copy an internal package object into another internal
package object, when it fails, the memory of acpi_operand_object
should be freed by the caller.

## References
- https://git.kernel.org/stable/c/01f2c2052ea50fb9a8ce12e4e83aed0267934ef0
- https://git.kernel.org/stable/c/02617006b5a46f2ea55ac61f5693c7afd7bf9276
- https://git.kernel.org/stable/c/02f237423c9c6a18e062de2d474f85d5659e4eb9
- https://git.kernel.org/stable/c/133462d35dae95edb944af86b986d4c9dec59bd1
- https://git.kernel.org/stable/c/470188b09e92d83c5a997f25f0e8fb8cd2bc3469
- https://git.kernel.org/stable/c/6fde666278f91b85d71545a0ebbf41d8d7af8074
- https://git.kernel.org/stable/c/c9125b643fc51b8e662f2f614096ceb45a0adbc3
- https://git.kernel.org/stable/c/dfdde4d5138bc023897033a5ac653a84e94805be
- https://git.kernel.org/stable/c/f51b2235e4f320edc839c3e5cb0d1f8a6e8657c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50423.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50423
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
