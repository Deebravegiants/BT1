# [M] firmware: qcom: uefisecapp: fix efivars registration race

## Summary
Severity: Medium
Advisory: CVE-2025-21998
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-21998
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: qcom: uefisecapp: fix efivars registration race

Since the conversion to using the TZ allocator, the efivars service is
registered before the memory pool has been allocated, something which
can lead to a NULL-pointer dereference in case of a racing EFI variable
access.

Make sure that all resources have been set up before registering the
efivars.

## References
- https://git.kernel.org/stable/c/c4e37b381a7a243c298a4858fc0a5a74e737c79a
- https://git.kernel.org/stable/c/da8d493a80993972c427002684d0742560f3be4a
- https://git.kernel.org/stable/c/f15a2b96a0e41c426c63a932d0e63cde7b9784aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21998.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21998
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
