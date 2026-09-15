# [M] CVE-2021-47434

## Summary
Severity: Medium
Advisory: CVE-2021-47434
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47434
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

xhci: Fix command ring pointer corruption while aborting a command

The command ring pointer is located at [6:63] bits of the command
ring control register (CRCR). All the control bits like command stop,
abort are located at [0:3] bits. While aborting a command, we read the
CRCR and set the abort bit and write to the CRCR. The read will always
give command ring pointer as all zeros. So we essentially write only
the control bits. Since we split the 64 bit write into two 32 bit writes,
there is a possibility of xHC command ring stopped before the upper
dword (all zeros) is written. If that happens, xHC updates the upper
dword of its internal command ring pointer with all zeros. Next time,
when the command ring is restarted, we see xHC memory access failures.
Fix this issue by only writing to the lower dword of CRCR where all
control bits are located.

## References
- https://git.kernel.org/stable/c/22bcb65ea41072ab5d03c0c6290e04e0df6d09a0
- https://git.kernel.org/stable/c/62c182b5e763e5f4062e72678e72ce3e02dd4d1b
- https://git.kernel.org/stable/c/dec944bb7079b37968cf69c8a438f91f15c4cc61
- https://git.kernel.org/stable/c/e54abefe703ab7c4e5983e889babd1447738ca42
- https://git.kernel.org/stable/c/ff0e50d3564f33b7f4b35cadeabd951d66cfc570
- https://git.kernel.org/stable/c/01c2dcb67e71c351006dd17cbba86c26b7f61eaf
