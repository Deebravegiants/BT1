# [H] acpi: nfit: fix narrowing conversion in acpi_nfit_ctl

## Summary
Severity: High
Advisory: CVE-2025-22044
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22044
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

acpi: nfit: fix narrowing conversion in acpi_nfit_ctl

Syzkaller has reported a warning in to_nfit_bus_uuid(): "only secondary
bus families can be translated". This warning is emited if the argument
is equal to NVDIMM_BUS_FAMILY_NFIT == 0. Function acpi_nfit_ctl() first
verifies that a user-provided value call_pkg->nd_family of type u64 is
not equal to 0. Then the value is converted to int, and only after that
is compared to NVDIMM_BUS_FAMILY_MAX. This can lead to passing an invalid
argument to acpi_nfit_ctl(), if call_pkg->nd_family is non-zero, while
the lower 32 bits are zero.

Furthermore, it is best to return EINVAL immediately upon seeing the
invalid user input.  The WARNING is insufficient to prevent further
undefined behavior based on other invalid user input.

All checks of the input value should be applied to the original variable
call_pkg->nd_family.

[iweiny: update commit message]

## References
- https://git.kernel.org/stable/c/2ff0e408db36c21ed3fa5e3c1e0e687c82cf132f
- https://git.kernel.org/stable/c/4b65cff06a004ac54f6ea8886060f0d07b1ca055
- https://git.kernel.org/stable/c/73851cfceb00cc77d7a0851bc10f2263394c3e87
- https://git.kernel.org/stable/c/85f11291658ab907c4294319c8102450cc75bb96
- https://git.kernel.org/stable/c/92ba06aef65522483784dcbd6697629ddbd4c4f9
- https://git.kernel.org/stable/c/bae5b55e0f327102e78f6a66fb127275e9bc91b6
- https://git.kernel.org/stable/c/c90402d2a226ff7afbe1d0650bee8ecc15a91049
- https://git.kernel.org/stable/c/e71a57c5aaa389d4c3c82f920761262efdd18d38
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22044.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22044
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
