# [M] CVE-2025-29364

## Summary
Severity: Medium
Advisory: CVE-2025-29364
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-08-28
Source: https://osv.dev/vulnerability/CVE-2025-29364
Type: osv

## Details
spimsimulator spim v9.1.24 and before is vulnerable to Buffer Overflow in the READ_SYSCALL and WRITE_SYSCALL system calls. The application verifies the legitimacy of the starting and ending addresses for memory read/write operations. By configuring the starting and ending addresses for memory read/write to point to distinct memory segments within the virtual machine, it is possible to circumvent these checks.

## References
- https://gist.github.com/Giles-one/a398e3da21ea9567970c6f0de543c3b3
- https://github.com/Giles-one/spimsimulatorEscape?tab=readme-ov-file#bug2-bypass-check-in-read_syscall-and-write_syscall-leading-to-out-of-bounds-readwrite
