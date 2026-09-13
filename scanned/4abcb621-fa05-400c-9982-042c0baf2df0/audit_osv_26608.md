# [H] ACPICA: Add AML_NO_OPERAND_RESOLVE flag to Timer

## Summary
Severity: High
Advisory: CVE-2023-53395
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53395
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.197, >=5.11.0 <5.15.133, >=5.16.0 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPICA: Add AML_NO_OPERAND_RESOLVE flag to Timer

ACPICA commit 90310989a0790032f5a0140741ff09b545af4bc5

According to the ACPI specification 19.6.134, no argument is required to be passed for ASL Timer instruction. For taking care of no argument, AML_NO_OPERAND_RESOLVE flag is added to ASL Timer instruction opcode.

When ASL timer instruction interpreted by ACPI interpreter, getting error. After adding AML_NO_OPERAND_RESOLVE flag to ASL Timer instruction opcode, issue is not observed.

=============================================================
UBSAN: array-index-out-of-bounds in acpica/dswexec.c:401:12 index -1 is out of range for type 'union acpi_operand_object *[9]'
CPU: 37 PID: 1678 Comm: cat Not tainted
6.0.0-dev-th500-6.0.y-1+bcf8c46459e407-generic-64k
HW name: NVIDIA BIOS v1.1.1-d7acbfc-dirty 12/19/2022 Call trace:
 dump_backtrace+0xe0/0x130
 show_stack+0x20/0x60
 dump_stack_lvl+0x68/0x84
 dump_stack+0x18/0x34
 ubsan_epilogue+0x10/0x50
 __ubsan_handle_out_of_bounds+0x80/0x90
 acpi_ds_exec_end_op+0x1bc/0x6d8
 acpi_ps_parse_loop+0x57c/0x618
 acpi_ps_parse_aml+0x1e0/0x4b4
 acpi_ps_execute_method+0x24c/0x2b8
 acpi_ns_evaluate+0x3a8/0x4bc
 acpi_evaluate_object+0x15c/0x37c
 acpi_evaluate_integer+0x54/0x15c
 show_power+0x8c/0x12c [acpi_power_meter]

## References
- https://git.kernel.org/stable/c/23c67fa615c52712bfa02a6dfadbd4656c87c066
- https://git.kernel.org/stable/c/2f2a5905303ae230b5159fcd8cdcd5b3e7ad5e2d
- https://git.kernel.org/stable/c/3a21ffdbc825e0919db9da0e27ee5ff2cc8a863e
- https://git.kernel.org/stable/c/3bf4463e40a17a23f2f261dfd7fe23129bdd04a4
- https://git.kernel.org/stable/c/430787056dd3c591eb553d5c3b2717efcf307d4e
- https://git.kernel.org/stable/c/625c12dc04a607b79f180ef3ee5a12bf2e3324c0
- https://git.kernel.org/stable/c/b102113469487b460e9e77fe9e00d49c50fe8c86
- https://git.kernel.org/stable/c/e1f686930ee4b059c7baa3c3904b2401829f2589
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53395.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53395
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
