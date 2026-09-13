# [M] CVE-2021-46940

## Summary
Severity: Medium
Advisory: CVE-2021-46940
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46940
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

tools/power turbostat: Fix offset overflow issue in index converting

The idx_to_offset() function returns type int (32-bit signed), but
MSR_PKG_ENERGY_STAT is u32 and would be interpreted as a negative number.
The end result is that it hits the if (offset < 0) check in update_msr_sum()
which prevents the timer callback from updating the stat in the background when
long durations are used. The similar issue exists in offset_to_idx() and
update_msr_sum(). Fix this issue by converting the 'int' to 'off_t' accordingly.

## References
- https://git.kernel.org/stable/c/337b1546cde87fb8588ddaedf0201b769baa572a
- https://git.kernel.org/stable/c/dbdf22fc825fdb1d97f23230064e0f9819471628
- https://git.kernel.org/stable/c/ea6803ff2cd1a2d7d880256bf562172b708a76ff
- https://git.kernel.org/stable/c/13a779de4175df602366d129e41782ad7168cef0
