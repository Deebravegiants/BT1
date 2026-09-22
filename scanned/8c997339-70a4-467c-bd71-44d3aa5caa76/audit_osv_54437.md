# [M] CVE-2023-6238

## Summary
Severity: Medium
Advisory: CVE-2023-6238
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-6238
Type: osv

## Details
A buffer overflow vulnerability was found in the NVM Express (NVMe) driver in the Linux kernel. Only privileged user could specify a small meta buffer and let the device perform larger Direct Memory Access (DMA) into the same buffer, overwriting unrelated kernel memory, causing random kernel crashes and memory corruption.

## References
- https://access.redhat.com/security/cve/CVE-2023-6238
- https://bugzilla.redhat.com/show_bug.cgi?id=2250834
