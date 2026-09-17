# [H] Contrast BadAML injection allows arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-g9ww-x58f-9g6m
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-g9ww-x58f-9g6m
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/contrast` — affected >=0 <1.18.0

## Details
# BadAML

BadAML is an AML injection attack that exploits the ACPI interface and allows arbitrary code execution in a confidential VM. The attack was first published in 2024:

- <https://blackhat.com/eu-24/briefings/schedule/#aml-injection-attacks-on-confidential-vms-42723>
- <https://dl.acm.org/doi/pdf/10.1145/3719027.3765123>

## Impact

An attacker with control over the host (which is assumed in the attacker model of Contrast) can execute malicious AML code to gain arbitrary code execution within the confidential guest.

AML is byte code embedded in ACPI tables that are passed from the host (QEMU) to the guest firmware (OVMF), and then passed from OVMF to the Linux kernel. The Linux kernel has an interpreter that executes the AML code. An attacker can craft a table with malicious AML code and the kernel will execute it. AML is Turing-complete and the interpreter has access to the full guest memory, including private pages.

See the [paper](https://dl.acm.org/doi/pdf/10.1145/3719027.3765123) for a detailed description and background of the attack.

Note that this is not a vulnerability specific to Contrast, but rather a generic vulnerability in Confidential Computing setups that use the ACPI interface.

## Affected platforms

This issue affects the SNP platforms supported by Contrast: `Metal-QEMU-SNP` and `Metal-QEMU-SNP-GPU`.
Users on these platforms should switch to the fixed Contrast version immediately.

`Metal-QEMU-TDX` isn't affected, as the content of the ACPI tables is covered by the runtime measurements (measured into RTMR 0 by OVMF) on Intel TDX.

## Patches

A sandbox similar to the one proposed in the paper has been implemented in the Linux kernel used by Contrast. The sandbox denies access to private memory pages by doing a page table lookup on every read/write by the AML interpreter.

This mitigates the attack completely: While an attacker can still run AML code, the code cannot read or modify private memory pages. Shared pages are readable/writable by the host hypervisor anyway.

## References
- https://github.com/edgelesssys/contrast/security/advisories/GHSA-g9ww-x58f-9g6m
- https://blackhat.com/eu-24/briefings/schedule/#aml-injection-attacks-on-confidential-vms-42723
- https://dl.acm.org/doi/pdf/10.1145/3719027.3765123
- https://github.com/edgelesssys/contrast
