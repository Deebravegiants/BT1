# [M] CVE-2021-47453

## Summary
Severity: Medium
Advisory: CVE-2021-47453
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47453
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: Avoid crash from unnecessary IDA free

In the remove path, there is an attempt to free the aux_idx IDA whether
it was allocated or not.  This can potentially cause a crash when
unloading the driver on systems that do not initialize support for RDMA.
But, this free cannot be gated by the status bit for RDMA, since it is
allocated if the driver detects support for RDMA at probe time, but the
driver can enter into a state where RDMA is not supported after the IDA
has been allocated at probe time and this would lead to a memory leak.

Initialize aux_idx to an invalid value and check for a valid value when
unloading to determine if an IDA free is necessary.

## References
- https://git.kernel.org/stable/c/73e30a62b19b9fbb4e6a3465c59da186630d5f2e
- https://git.kernel.org/stable/c/777682e59840e24e6c5672197e6ffbcf4bff823b
