# [H] CVE-2021-47048

## Summary
Severity: High
Advisory: CVE-2021-47048
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47048
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: spi-zynqmp-gqspi: fix use-after-free in zynqmp_qspi_exec_op

When handling op->addr, it is using the buffer "tmpbuf" which has been
freed. This will trigger a use-after-free KASAN warning. Let's use
temporary variables to store op->addr.val and op->cmd.opcode to fix
this issue.

## References
- https://git.kernel.org/stable/c/1231279389b5e638bc3b66b9741c94077aed4b5a
- https://git.kernel.org/stable/c/23269ac9f123eca3aea7682d3345c02e71ed696c
- https://git.kernel.org/stable/c/a2c5bedb2d55dd27c642c7b9fb6886d7ad7bdb58
- https://git.kernel.org/stable/c/d67e0d6bd92ebbb0294e7062bbf5cdc773764e62
